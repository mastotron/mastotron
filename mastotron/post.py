from .imports import *
from .postlist import PostList
from .htmlfmt import to_html

in_reply_to_uri_key = 'in_reply_to__id'

def Post(url_or_uri_x, **post_d):
    from mastotron import Tron
    return Tron().post(url_or_uri_x, **post_d)

class PostModel(DictModel):
    def __init__(self,*x,**y):
        super().__init__(*x,**y)
        # self.save()

    def __eq__(self, post):
        return self._id == post._id

    def __hash__(self):
        return hash(self._id)


    @property
    def uri(self):
        return self._data.get('url')

    def is_valid(self):
        return bool(self.uri)

    @property
    def server(self):
        return parse_account_name(self.url)[-1]
    @property
    def un(self):
        return parse_account_name(self.url)[-1]

    def api(self):
        from mastotron import Tron
        return Tron().api_server(self.server)
    

    @property
    def author(self):
        from .poster import Poster
        return Poster(self.account)

    # def get_url_local(self, server):
        # return '/'.join([server,'@'+self.acct])
    
    @property
    def timestamp(self):
        return self._data.get(
            'timestamp',
            int(round(self.datetime.timestamp()))
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

    def get_posts_above(self, as_list=True):
        pre,post=self.status_context
        l=[Post(d.get('url'), **d) for d in pre]
        return PostList(l) if not as_list else l
    
    def get_posts_below(self, as_list=True):
        pre,post=self.status_context
        l=[Post(d.get('url'), **d) for d in post]
        return PostList(l) if not as_list else l
    
    @cached_property
    def above(self):
        return self.get_posts_above(as_list=False)
    
    @property
    def below(self): 
        return self.get_posts_below(as_list=False)

    @property
    def context(self): return self.get_context()

    def get_context(self, as_list=False, recurse=1):
        posts=self.get_posts_above() + self.get_posts_below()
        if recurse>0:
            if self.op != self and self.op not in set(posts):
                posts.append(self.op)
            
            for post in [x for x in posts]:
                posts.extend(post.get_context(recurse=recurse-1, as_list=True))
        posts.append(self)
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

    def get_context_d(self):
        pre,post = self.status_context
        return {
            postd['id'] : postd
            for postd in pre + post
        }


    @cached_property
    def in_reply_to(self):
        if not self.in_reply_to_id: return

        context_d = self.get_context_d()
        if self.in_reply_to_id in context_d:
            reply_d = context_d[self.in_reply_to_id]
            return Post(reply_d['url'], **reply_d)
        else:
            if self.above:
                return self.above[0]

    @property
    def replies(self):
        return PostList(Post(idx) for idx in [*set(self._data.get('replies_uri',[]))])

    @cached_property
    def op(self):
        if self.in_reply_to: return self.in_reply_to.op
        return self
                    
    def __repr__(self): return f"Post('{self._id}')"
    def _repr_html_(self): return self.html

    @property
    def html(self):
        
        return post_to_html(self, allow_embedded=False)
    
    @property
    def num_reblogs(self):
        if self.is_boost and self.in_boost_of: 
            res = self.in_boost_of.num_reblogs
        else:
            res = self.reblogs_count
        return res if res else 0
    
    @property
    def num_likes(self):
        if self.is_boost and self.in_boost_of: 
            res = self.in_boost_of.num_likes
        else:
            res = self.favourites_count
        return res if res else 0
    
    @property
    def num_replies(self):
        if self.is_boost and self.in_boost_of: 
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

    def score(self, score_type='All'):
        return self.scores.get(score_type,np.nan)

    @property
    def text(self):
        return unhtml(self.content).strip()

    @property
    def label(self, limsize=40):
        # from unidecode import unidecode
        import html
        stext = self.spoiler_text
        if not stext: stext=' '.join(w for w in self.text.split() if w and w[0]!='@')
        return html.unescape(stext)[:limsize].strip()

    def save(self):
        data = self.data
        from .db import TronDB
        # log.debug(f'saving: {self}')
        TronDB().set_post(data)

    @cached_property
    def data(self):
        return {
            **self._data,
            **{'timestamp':self.timestamp},
            **{f'score_{k}':v for k,v in self.scores.items()},
            **{'_id':self._id},
        }

    @cached_property
    def node_data(self):
        odx={}
        odx['html'] = to_html(self, allow_embedded=False)
        odx['shape']='box'
        odx['label']=self.label
        odx['text'] = self.text
        odx['node_type']='post'
        odx['color'] = '#1f465c' if not self.is_reply else '#061f2e'
        return odx


