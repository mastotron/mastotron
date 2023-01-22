from .imports import *
from .postlist import PostList
from .htmlfmt import to_html
from .db import TronDB

in_reply_to_uri_key = 'in_reply_to__id'

def Post(url_or_uri_x, **post_d):
    if not url_or_uri_x: return
    if type(url_or_uri_x) is PostModel: return url_or_uri_x
    
    from .mastotron import Tron
    return Tron().post(url_or_uri_x, **post_d)


@total_ordering
class PostModel(DictModel):
    def __init__(self,*x,**y):
        super().__init__(*x,**y)
        self.boot()

    def __eq__(self, post):
        post=Post(post)
        return type(post) is PostModel and self._id==post._id

    def __hash__(self):
        return hash(self._id)

    def __gt__(self, other):
        return self.timestamp > other.timestamp

    def boot(self):
        if self._id and self.urli and self._id != self.urli:
            self.set_is_copy_of(self.urli)
        return self

    @property
    def urli(self):
        return self.url if self.url else self.uri

    def set_is_copy_of(self, post_or_uri):
        post=Post(post_or_uri)
        if post:
            self.relate(
                post,
                REL__IS_LOCAL_COPY_OF
            )

    @property
    def is_valid(self):
        return bool(self._id) and bool(self.author) and bool(self.author._id)

    @cached_property
    def server(self):
        return parse_account_name(self.url)[-1]
    @cached_property
    def un(self):
        return parse_account_name(self.url)[0]
    @cached_property
    def acct(self):
        return f'{self.un}@{self.server}'


    def api(self):
        from .mastotron import Tron
        return Tron().api_server(self.server)
    

    @property
    def author(self):
        from .poster import Poster
        return Poster(self.account, _id=self.acct)

    def get_url_local(self, server):
        from .mastotron import Tron
        cache=Tron().cache('url_to_uri')
        return cache.get(f'{self._id}__in__{server}')
    
    @property
    def timestamp(self):
        return self._data.get(
            'timestamp',
            self.datetime.timestamp()
        )

    @cached_property
    def datetime(self):
        if type(self.created_at) is str:
            from dateutil.parser import parse
            return parse(self.created_at)
        else:
            return self.created_at
    
    @property
    def datetime_str(self):
        return self.datetime.strftime("%m/%d/%Y at %H:%M:%S")
        
    @cached_property
    def post_id(self):
        return os.path.join(self.poster_id, self.url.split('/')[-1])
    
    @cached_property
    def status_id(self):
        return self.url.split('/')[-1]

    @cached_property
    def poster_id(self):
        return self.author.account
        
    @cached_property
    def in_boost_of(self):
        if self.reblog:
            url = self.reblog.get('url')
            if url:
                post = Post(url, **dict(self.reblog))
                if post:
                    return post


    def wider_context(self): return self.get_context(recurse=True)
    def immediate_context(self): return self.get_context(recurse=False)
    convo = immediate_context

    def _get_posts_abovebelow(self, pre=True, as_list=True):
        try:
            _pre,_post=self.status_context
            l=[Post(d.get('url'), **d) for d in (_pre if pre else _post)]
        except Exception as e:
            log.error(e)
            l=[]
        return PostList(l) if not as_list else l

    @cache
    def get_posts_above(self, as_list=True):
        return self._get_posts_abovebelow(pre=True, as_list=as_list)
    @cache
    def get_posts_below(self, as_list=True):
        return self._get_posts_abovebelow(pre=False, as_list=as_list)
    
    @cached_property
    def above(self):
        return self.get_posts_above(as_list=False)
    
    @cached_property
    def below(self): 
        return self.get_posts_below(as_list=False)

    @cached_property
    def context(self):
        return self.get_context(
            as_list=False,
            recurse=0,
            interrelate=False,
            progress=True
        )
    
    @cached_property
    def thread(self):
        return self.get_context(
            as_list=False,
            recurse=0,
            interrelate=True,
            progress=False
        )
    
    

    
    @cache
    def get_context_op(self):
        return self.op.get_context() if self.op != self else []


    def iter_context(self, recurse=0, progress=False, lim=None,**kwargs):
        done=set()

        def postiter():
            yield from reversed(self.get_posts_above())
            yield self
            yield from self.get_posts_below()
        iterr=postiter()
        if progress: iterr=tqdm(iterr, desc='Iterating context')        
        for post in iterr:
            if post!=self and post not in done:
                done.add(post)
                yield post
                if lim and len(done)>=lim: break
        
        # for post in {x for x in done}:
        #     if not lim or len(done)<lim:
        #         post2_iter = post.iter_context(
        #             recurse=recurse-1 if recurse>0 else 0,
        #             progress=False,
        #             lim=lim if not lim else lim-len(done),
        #             **kwargs
        #         )
        #         for post2 in post2_iter:
        #             if post2 not in done:
        #                 done.add(post2)
        #                 yield post2
        #                 if lim and len(done)>=lim: break
        

    def get_context(self, as_list=True, recurse=0, interrelate=False, progress=False, lim=None):
        posts=list(self.iter_context(recurse=recurse, progress=progress,lim=lim))
        if interrelate: self.interrelate(posts=posts)
        return PostList(posts) if not as_list else posts

    @cached_property
    def status_context(self):
        from .mastotron import Tron
        from .postlist import PostList

        res = Tron().status_context(self._id)
        if not res: return [], []

        posts_pre=res.get('ancestors',[])
        posts_post=res.get('descendants',[])

        return posts_pre, posts_post

    @cache
    def get_context_d(self, recurse=0):
        posts = self.get_context(recurse=recurse, as_list=True, interrelate=False)
        return dict((post._id, post) for post in posts)

    def interrelate(self, 
            posts = None, 
            recurse=0, 
            force=False, 
            progress=False, 
            **kwargs):
        
        if force or not self._related:
            if not posts: 
                posts = self.get_context(
                    recurse=recurse, 
                    interrelate=False
                )
            
            iterr = posts if not progress else tqdm(
                posts,
                desc='Relating context'
            )
            for post in iterr: 
                post.get_in_reply_to(force=force)
            
            self._related=True
    
    


    @property
    def in_reply_to(self):
        return self.get_in_reply_to(force=False)
    

    def get_in_reply_to(self, force=False, save=True):
        if not self.is_reply: return

        if not force:    
            reply_id_from_db = self._get_in_reply_to_id_from_gdb()
            if reply_id_from_db: return Post(reply_id_from_db)

        post = self._get_in_reply_to_from_context()
        if post and save: self._set_in_reply_to_id_in_gdb(post)
        
        return post



    def _get_in_reply_to_id_from_gdb(self):
        log.debug('_get_in_reply_to_id_from_gdb')
        return TronDB().get_relative(self, 'in_reply_to')
    def _set_in_reply_to_id_in_gdb(self, post):
        log.debug('_set_in_reply_to_id_in_gdb')
        return TronDB().relate(self, post, 'in_reply_to')
    
    def _get_in_reply_to_from_context(self):
        log.debug('_get_in_reply_to_from_context')
        context_d = self.get_context_d()
        post = context_d.get(self.in_reply_to_id)
        if not post:
            above = self.get_posts_above(as_list=True)
            if above:
                post = above[-1]
        return post


    @property
    def db(self):
        from .db import TronDB
        return TronDB()
    @property
    def gdb(self):
        from .db import TronDB
        return TronDB().gdb

    def relate(self, post2, rel):
        from .db import TronDB
        return self.db.relate(self, post2, rel)
    
    def relations_out(self, rel):
        return [Post(d.get('id')) for d in self.gdb.v(self._id).out(rel).all().get('result') if d.get('id')]
    def relations_inc(self, rel):
        return [Post(d.get('id')) for d in self.gdb.v(self._id).inc(rel).all().get('result') if d.get('id')]
    def relations(self, rel):
        return self.relations_out(rel) + self.relations_inc(rel)

    
    
    @cached_property
    def source(self):
        l=self.relations_out(REL__IS_LOCAL_COPY_OF)
        return l[0] if l else None
    
    @cached_property
    def copies(self):
        l=self.relations_inc(REL__IS_LOCAL_COPY_OF)
        return l if l else []

    @cached_property
    def replies(self):
        return PostList(Post(idx) for idx in [*set(self._data.get('replies_uri',[]))])

    @cached_property
    def op(self):
        if self.in_reply_to: return self.in_reply_to.op
        return self
                    
    def __repr__(self): return f"Post('{self._id}')"
    def _repr_html_(self): return self.html

    def get_html(self, allow_embedded=False, server=None):
        from .htmlfmt import post_to_html
        return post_to_html(
            self, 
            allow_embedded=allow_embedded,
        )
    
    @property
    def num_reblogs(self):
        if False: # self.is_boost and self.in_boost_of: 
            res = self.in_boost_of.num_reblogs
        else:
            res = self.reblogs_count
        return res if res else 0
    
    @property
    def num_likes(self):
        if False: #self.is_boost and self.in_boost_of: 
            res = self.in_boost_of.num_likes
        else:
            res = self.favourites_count
        return res if res else 0
    
    @property
    def num_replies(self):
        if False: #self.is_boost and self.in_boost_of: 
            res = self.in_boost_of.num_replies
        else:
            res = self.replies_count
        return res if res else 0

    @property
    def is_boost(self):
        return self.reblog is not None
    @property
    def is_reply(self):
        return self.in_reply_to_id is not None

    @property
    def datetime_str(self):
        return self.datetime.strftime("%m/%d/%Y at %H:%M:%S")

    @property
    def datetime_str_h(self):
        import human_readable as humr
        return humr.date_time(
            datetime.now().timestamp() - self.timestamp
        )
    

    @cached_property
    def scores(self):
        """
        These scoring ideas come from mastodon_digest (https://github.com/hodgesmr/mastodon_digest).
        """
        scores={}

        # simple score
        scores['Simple'] = gmean([
            self.num_reblogs+1, 
            self.num_likes+1,
        ])

        # extended simple score
        scores['ExtendedSimple'] = gmean([
            self.num_reblogs+1, 
            self.num_likes+1,
            self.num_replies+1
        ])

        # add weighted versions
        for score_name in list(scores.keys()):
            scores[score_name+'Weighted'] = scores[score_name] / sqrt(self.author.num_followers+1)

        scores['All'] = gmean(list(scores.values()))
        return scores

    @property
    def score(self):
        return self.get_score()

    def get_score(self, score_type='All'):
        return self.scores.get(score_type,np.nan)

    @property
    def text(self):
        return unhtml(self.content).strip()

    @property
    def label(self): return self.get_label()

    def get_label(self, limsize=40, limwords=4, replace_urls=True):
        import html
        #stext = self.spoiler_text
        #if not stext: 
        stext=' '.join(w for w in self.text.split() if w and w[0]!='@')
        stext=html.unescape(stext).strip()
        if limwords: stext=' '.join(stext.split()[:limwords])
        if replace_urls: stext=' '.join(w.split('://',1)[-1][:20] if w.startswith('http') else w for w in stext.split())
        if limsize: stext=stext[:limsize]

        return stext.strip()

    def save(self):
        # data = {str(k):str(v) for k,v in self.data.items()}
        from .db import TronDB
        # log.debug(f'saving: {self}')
        TronDB().set_post(self.data)
        # TronDB().gdb.updatej(data)

    def mark_read(self):
        # save in self
        self._data['is_read']=True
        self.save()

        # save in boost
        if self.is_boost and self.in_boost_of:
            self.in_boost_of.mark_read()
        
        # save in source if any
        if self.source:
            self.source.mark_read()
    
    def mark_unread(self):
        self._data['is_read']=False
        self.save()
    
    @property
    def is_read(self):
        if self.is_boost and self.in_boost_of:
            return self.in_boost_of.is_read
        if self.source:
            return self.source.is_read
        return self._data.get('is_read', False)
    

    
    @property
    def data_default(self):
        return {'_id':self._id, 'is_read':False}

    @cached_property
    def data(self):
        od={
            **self.data_default,
            **self._data,
            **{'timestamp':self.timestamp},
            **{f'score_{k}':v for k,v in self.scores.items()},
            **{'_id':self._id},
        }
        # if self.source: od={**od, **self.source.data}
        return od

    @cached_property
    def node_data(post):
        odx={}
        odx['_id'] = post._id
        odx['id']=post.url if post.url else post.uri
        odx['html'] = post.get_html(allow_embedded=False)
        odx['shape'] = 'circularImage' # if not same_author else 'box'
        odx['image'] = post.author.avatar
        odx['label']=post.label if not post.is_boost else ''
        odx['text'] = post.text if not post.is_boost else 'RT'
        odx['node_type']='post'
        odx['scores'] = post.scores
        odx['score'] = post.scores.get(SCORE_TYPE, np.nan)
        odx['timestamp'] = post.timestamp
        # odx['fixed']=dict(x=False,y=False)
        odx['num_replies'] = post.num_replies
        odx['is_read']=post.is_read
        odx['is_reply']=post.is_reply
        odx['is_boost']=post.is_boost
        return odx


