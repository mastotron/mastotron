from .imports import *
from .postlist import PostList
from .htmlfmt import to_html
from .db import TronDB

is_reply_to_uri_key = 'is_reply_to__id'

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
    
    def __str__(self): return self._id
    def __repr__(self): return f"Post('{self._id}')"
    def _repr_html_(self): return self.html

    ############
    ### BOOT ###
    ############

    def boot(self):
        if not self.out(REL_GRAPHTIME):
            self.store_graphtime()
        
        # if not self.out(REL_READ_STATUS):
            # self.mark_unread()
    


    ############
    ### TIME ###
    ############

    @cached_property
    def graphtime(self):
        return get_graphtime_str(self.timestamp)
    @property
    def graphtime_iter(self):
        yield from iter_graphtimes(self.timestamp)
    
    @property
    def graphtime_indb(self):
        return self.out(REL_GRAPHTIME)
    def store_graphtime(self):
        if not self.graphtime_indb:
            TronDB().relate(self, self.graphtime, REL_GRAPHTIME)

    #############
    ### LOCAL ###
    #############

    @cached_property
    def is_local_for(self):
        if self.is_local:
            out = Post(self.out(REL_IS_LOCAL_FOR))
            if not out:
                out = Post(self.urli, **self._data)
                self.relate(out,REL_IS_LOCAL_FOR)
            return out

    @cached_property
    def source(self):
        return self.is_local_for if self.is_local_for else self
    @property
    def is_source(self):
        return self.source == self
    
    @cached_property
    def copies(self):
        return PostList(self.incs(REL_IS_LOCAL_FOR))
    @cached_property
    def local(self):
        if self.is_local: return self
        if self.copies: return self.copies[0]
    
    @cached_property
    def allcopies(self):
        l=[self.source] + list(self.source.copies) + [self.in_boost_of]
        return {x for x in l if x is not None and type(x) is PostModel}
    
    def get_local(self, server):
        copies = [p for p in self.source.copies if p.localserver==server]
        return copies[0] if copies else None

    @property
    def localsource(self):
        if self.local: return self.local
        return self.source
    def get_localsource(self, server):
        copies = [p for p in self.source.copies if p.localserver==server]
        return copies[0] if copies else self.source
    
    
    #############
    ### BOOST ###
    #############
    
    @cached_property
    def is_boost_of(self):
        if self.is_boost:
            out = Post(self.out(REL_IS_BOOST_OF))
            if not out:
                url = self.reblog.get('url')
                out = Post(url, **dict(self.reblog))
                self.relate(out,REL_IS_BOOST_OF)
            return out

    @cached_property
    def was_boosted_by(self):        
        if not self.is_boost:
            return map(Post,self.incs(REL_IS_BOOST_OF))
    


    #############
    ### REPLY ###
    #############

    @cached_property
    def is_reply_to(self):
        if self.is_reply:
            out = Post(self.out(REL_IS_REPLY_TO))
            if not out:
                # otherwise let's get from context?
                status_d = self.is_reply_to_status
                url = status_d.get('url')
                if status_d and url:
                    out = Post(url, **status_d)
                    self.relate(out, REL_IS_REPLY_TO)
            return out
    
    @cached_property
    def was_replied_to(self):
        return PostList(self.incs(REL_IS_REPLY_TO))

    ##########
    # READ?? #
    ##########

    def mark_read(self):
        # for post in self.allcopies:
        # TronDB().unrelate(self, NODE_READ_STATUS_IS_UNREAD, REL_READ_STATUS)
        TronDB().relate(self, NODE_READ_STATUS_IS_READ, REL_READ_STATUS)
    
    def mark_unread(self):
        # for post in self.allcopies:
        # TronDB().unrelate(self, NODE_READ_STATUS_IS_READ, REL_READ_STATUS)
        TronDB().relate(self, NODE_READ_STATUS_IS_UNREAD, REL_READ_STATUS)
    
    @property
    def is_read(self):
        for post in self.allcopies:
            nstatus=post.out(REL_READ_STATUS)
            if nstatus is not None:
                return nstatus == NODE_READ_STATUS_IS_READ
    
    



    @property
    def urli(self):
        return to_uri(self.url if self.url else self.uri)

    @property
    def is_valid(self):
        return bool(self._id) and bool(self.author) and bool(self.author._id)

    @cached_property
    def server(self):
        return parse_account_name(self.url)[-1]
    @cached_property
    def localserver(self):
        return self._id.split('://',1)[-1].split('/')[0]
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
    def status_context(self):
        from .mastotron import Tron
        tron = Tron()

        res = tron.status_context(self._id)
        if not res: return [], []

        posts_pre=res.get('ancestors',[])
        posts_post=res.get('descendants',[])

        ## quick store?
        for status_d in posts_pre+posts_post:
            url = status_d.get('url')
            tron.status(url, **status_d)
            tron.status_context(url, **res)

        return posts_pre, posts_post

    @cache
    def status_context_d(self, key='id'):
        pre,post=self.status_context
        return dict((d.get(key),d) for d in pre+post)

    @property
    def is_reply_to_status(self):
        o={}
        if self.is_reply and self.in_reply_to_id:
            o=self.status_context_d().get(self.in_reply_to_id)
            if not o:
                pre,post=self.status_context
                if pre:
                    o=pre[-1]
        return o


    def iter_context(self):
        posts_pre,posts_post = self.status_context
        def yield_dicts():
            yield from reversed(posts_pre)
            yield from posts_post
        def yield_posts():
            yield self
            for d in yield_dicts(): 
                post = Post(d.get('url'), **d)
                yield post
        yield from yield_posts()

    def iter_contexts(self,**kwargs):
        for post in self.allcopies:
            yield from post.iter_context(**kwargs)

    def get_context(self, lim=None, **kwargs):
        return PostList(self.iter_contexts(**kwargs), lim=lim)

    @cached_property
    def context(self): return self.get_context()


    def relate(self, post2, rel):
        post2=Post(post2)
        if post2 and rel: return TronDB().relate(self, post2, rel)
    
    def inc(self, rel): return TronDB().get_rel_inc(self,rel)
    def incs(self, rel): return TronDB().get_rels_inc(self,rel)
    def out(self, rel): return TronDB().get_rel_out(self,rel)
    def outs(self, rel): return TronDB().get_rels_out(self,rel)
    def alls(self, rel): return self.incs(rel) + self.outs(rel)
    
    def rels_exist(self):
        v=TronDB().gdb.v(self._id)
        incs=v.inc().all().get('result')
        outs=v.out().all().get('result')
        return bool(incs) or bool(outs)
    


    @cached_property
    def replies(self):
        return PostList(self.was_replied_to)

    @cached_property
    def convo(self):
        return self.context + self.reply_chain
        # self.get_context()
        # return PostList([self] + [self.is_reply_to] + self.was_replied_to) + self.reply_chain
    

    @cached_property
    def op(self):
        if self.is_reply_to:
            print(f'searching for OP in {self.is_reply_to}')
            return self.is_reply_to.op
        return self


    def iter_reply_chain(self):
        yield self
        if self.is_reply_to:
            yield from self.is_reply_to.iter_reply_chain()
    
    @cached_property
    def reply_chain(self):
        return PostList(self.iter_reply_chain())
    
    @property
    def unread_reply_chain(self):
        return PostList(post for post in self.reply_chain if not post.is_read)
                    
    

    def get_html(self, allow_embedded=False, server=None):
        from .htmlfmt import post_to_html
        return post_to_html(
            self, 
            allow_embedded=allow_embedded,
        )
    
    @property
    def num_reblogs(self):
        if False: # self.is_boost and self.is_boost_of: 
            res = self.is_boost_of.num_reblogs
        else:
            res = self.reblogs_count
        return res if res else 0
    
    @property
    def num_likes(self):
        if False: #self.is_boost and self.is_boost_of: 
            res = self.is_boost_of.num_likes
        else:
            res = self.favourites_count
        return res if res else 0
    
    @property
    def num_replies(self):
        if False: #self.is_boost and self.is_boost_of: 
            res = self.is_boost_of.num_replies
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
    def is_local(self):
        return self.urli != self._id

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
        cache=self.cache
        from .db import TronDB
        # log.debug(f'saving: {self}')
        TronDB().set_post(self.data)
        # TronDB().gdb.updatej(data)


    
        
    
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
        odx['id'] = post._id
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


