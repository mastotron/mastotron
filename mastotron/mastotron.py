import os,sys; sys.path.insert(0,'..')
import numpy as np
from mastodon import Mastodon, AttribAccessDict
from datetime import datetime, timedelta, timezone
from scipy.stats import gmean
from math import sqrt
from pprint import pprint
import pandas as pd
from IPython.display import Markdown, display
def printm(x): display(Markdown(x))
import webbrowser,json, re
from collections import UserDict
def unhtml(x): 
    x = x.replace('<br>','\n')
    return re.sub(r'<.*?>', '', x).strip()
import networkx as nx
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


path_data = os.path.expanduser('~/.mastotron')
path_env = os.path.join(path_data, 'config.json')
app_name = 'mastotron'

API = None
def get_api():
    global API
    return API

def set_api(mastotron_obj):
    global API
    API = mastotron_obj

class Mastotron():
    def __init__(self, account_name, code=None):
        
        # get un and server from acct name
        self.username,self.servername = parse_account_name(account_name)
        self.code=code
        if not self.username or not self.servername:
            raise Exception('! Invalid account name !')

        set_api(self)

    @property
    def acct(self):
        return self.username+'@'+self.servername
    @property
    def acct_safe(self):
        return self.username+'__at__'+self.servername
    

    @property
    def server(self):
        return f'https://{self.servername}'

    @property
    def path_client_secret(self):
        return os.path.join(
            path_data,
            self.acct,
            f'clientcred.secret'
        )

    @property
    def path_user_secret(self):
        return os.path.join(
            path_data,
            self.acct,
            f'usercred.secret'
        )

    @property
    def api(self):
        if not hasattr(self,'_api'):
            # make sure app token exists
            self.init_app()

            # make sure user token exists
            self.init_user()

            # log in and set app
            self._api = Mastodon(access_token = self.path_user_secret)

        return self._api

    def init_app(self):
        if not os.path.exists(self.path_client_secret):
            if not os.path.exists(os.path.dirname(self.path_client_secret)):
                os.makedirs(os.path.dirname(self.path_client_secret))
            Mastodon.create_app(
                app_name,
                api_base_url = self.server,
                to_file = self.path_client_secret
            )

    def auth_request_url(self):
        self.init_app()
        api = Mastodon(client_id = self.path_client_secret)
        url=api.auth_request_url()
        return url

    def user_is_init(self):
        self.init_app()
        return os.path.exists(self.path_user_secret)

    def init_user(self, code=None):
        if code is None: code=self.code
        if not self.user_is_init():
            if not os.path.exists(os.path.dirname(self.path_user_secret)):
                os.makedirs(os.path.dirname(self.path_user_secret))
            
            if not os.path.exists(self.path_client_secret):
                self.init_app()

            api = Mastodon(client_id = self.path_client_secret)
            if not code:
                url=api.auth_request_url()
                webbrowser.open(url)
                code = input('Paste the code from the browser:\n')
            
            api.log_in(code = code, to_file = self.path_user_secret)

    def iter_timeline(self, max_posts=20, hours_ago=1,timeline_type='home'):
        # init vars
        total_posts_seen = 0
        # filters = self.api.filters()
        seen_post_urls = set()

        # Set our start query
        start = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        # get initial response
        timeline = self.api.timeline(timeline=timeline_type, min_id=start)
        # get filters
        while timeline and total_posts_seen < max_posts:
            # if filters: 
                # timeline = self.api.filters_apply(timeline, filters, "home")
            for post in timeline:
                total_posts_seen += 1

                if post.url not in seen_post_urls:
                    seen_post_urls.add(post.url)

                    yield Post(post, _tron=self)

            # keep going
            timeline = self.api.fetch_previous(timeline)

    def latest_post(self, **kwargs):
        iterr=self.iter_timeline(**kwargs)
        return next(iterr)

    def latest_posts(self, max_posts=20, **kwargs):
        iterr=self.iter_timeline(
            max_posts=max_posts, 
            **kwargs
        )
        return PostList(iterr)

    def timeline(self, **kwargs):
        return PostList(self.iter_timeline(**kwargs))

    def get_post(self, id):
        return Post(self.api.status(id), _tron=self)
    


class Post(AttribAccessDict):

    def __init__(self,*args,id=None,_tron=None,**kwargs):
        ## init self
        self._tron = (get_api() if not _tron else _tron)

        if id is not None:
            if not kwargs:
                kwargs = self._tron.api.status(id)
            else:
                kwargs['id'] = id
        
        ## pass into dict init
        super().__init__(*args, **kwargs)
        

        
        
    @property
    def in_boost_of(self):
        if not hasattr(self,'_post_reposted'):
            self._post_reposted = Post(self['reblog'], _tron=self._tron) if self['reblog'] else None
        return self._post_reposted

    
    @property
    def in_reply_to(self):
        if not hasattr(self,'_post_repliedto'):
            self._post_repliedto = Post(id=self['in_reply_to_id'], _tron=self._tron) if self['in_reply_to_id'] else None
        return self._post_repliedto
        
                

    def __repr__(self): return f'Post({self.id})'
    def _repr_html_(self, allow_embedded = True): 
        if self.is_boost:
            o = f'''
                <div class="post reblog">
                    <p>
                        {self.author._repr_html_()} reposted at {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.in_boost_of._repr_html_()}
                    <p>Post ID: <a href="{self.url_local}" target="_blank">{self.id}</a></p>

                </div>
            '''
        else:
            imgs_urls = [d.get('preview_url') for d in self.media_attachments]
            imgs = [
                f'<a href="{url}" target="_blank"><img src="{url}" /></a>'
                for url in imgs_urls
                if url
            ]

            o = f'''
                <div class="post origpost">
                    <p>
                        {self.author._repr_html_()} posted on {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.content}

                    <center>{"    ".join(imgs)}</center>
                    
                    <p>
                        {self.replies_count:,} 🗣
                        |
                        {self.reblogs_count:,} 🔁
                        |
                        {self.favourites_count:,} 💙
                        |
                        Post ID: <a href="{self.url_local}" target="_blank">{self.id}</a>
                    </p>

                    {"<p><i>... in reply to:</i></p> " + self.in_reply_to._repr_html_() + " <br/> " if allow_embedded and self.is_reply else ""}
                </div>
            '''
            
        return '\n'.join([ln.lstrip() for ln in o.split('\n')]).strip()

    @property
    def author(self):
        return Poster(self.get('account',{}), _tron=self._tron)

    
    @property
    def num_reblogs(self):
        if self.is_boost: return self.in_boost_of.num_reblogs
        return self.reblogs_count
    
    @property
    def num_likes(self):
        if self.is_boost: return self.in_boost_of.num_likes
        return self.favourites_count
    
    @property
    def num_replies(self):
        if self.is_boost: return self.in_boost_of.num_replies
        return self.replies_count

    @property
    def is_boost(self):
        return self.reblog is not None
    @property
    def is_reply(self):
        return self.in_reply_to_id is not None


    def scores(self):
        """
        These scoring ideas come from mastodon_digest (https://github.com/hodgesmr/mastodon_digest).
        """
        if not hasattr(self,'_scores'):
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
            self._scores = scores
        return self._scores

    def score(self, score_type='All'):
        return self.scores().get(score_type,np.nan)

    @property
    def text(self):
        return unhtml(self.content).strip()

    @property
    def label(self, limsize=40):
        stext = self.spoiler_text
        if not stext: stext=' '.join(w for w in self.text.split() if w and w[0]!='@')
        return stext[:limsize]

    @property
    def url_local(self):
        return self.get_url_local()
    
    def get_url_local(self):
        return '/'.join([
            self._tron.server,
            '@'+self.author.acct,
            str(self.id),
        ])



class Poster(AttribAccessDict):

    def __init__(self,*args,_tron=None,**kwargs):
        ## init self
        self._tron = (get_api() if not _tron else _tron)
        ## pass into dict init
        super().__init__(*args, **kwargs)

    
    def __hash__(self):
        return hash(self.acct)
    
    def __eq__(self, other):
        return self.acct == other.acct

    def __repr__(self):
        return f'Poster({self.acct})'

    def _repr_html_(self, allow_embedded=False, **kwargs):
        return f'<div class="author"><img src="{self.avatar}" /> <a href="{self.url_local}" target="_blank">{self.display_name}</a> ({self.followers_count:,} 👥){self.note if allow_embedded else ""}</div>'

    @property
    def num_followers(self):
        return self.followers_count

    @property
    def num_following(self):
        return self.following_count

    @property
    def url_local(self):
        return self.get_url_local()
    
    def get_url_local(self):
        return '/'.join([
            self._tron.server,
            '@'+self.acct,
        ])





from collections import UserList

class PostList(UserList):
    def __init__(self, l):
        super().__init__(l)
    
    def sort_chron(self):
        self.sort(key=lambda post: post.created_at, reverse=True)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    def network(self):
        return PostNet(self)

    @property
    def posters(self):
        return {post.author for post in self}




class PostNet:
    def __init__(self, posts):
        self.posts = (
            PostList(posts)
            if type(posts)!=PostList
            else posts
        )

    def graph(self):
        # start graph
        G=nx.DiGraph()
        # funcs
        node2int = {}
        int2node = {}
        def ensure_post_node(post):
            post_name = str(post)
            post_id = node2int.get(post_name)
            if post_id is None: post_id = G.order()+1

            if not G.has_node(post_id):    
                node2int[post_name]=post_id
                G.add_node(
                    post_id,
                    name=post_name,
                    node_type='post',
                    label=post.text[:50],
                    text=post.text,
                    url=post.url_local,
                    obj=post
                )
            return post_id

        def ensure_user_node(user):
            user_name = str(user)
            user_id = node2int.get(user_name)
            if user_id is None: user_id = G.order()+1
            if not G.has_node(user_id):
                node2int[user_name]=user_id

                G.add_node(
                    user_id,
                    name=user_name,
                    node_type='user',
                    label = user.display_name,
                    text = user.display_name,
                    obj = user,
                    url = user.url_local
                )
            return user_id
        
        def add_user_post(post):
            user = post.author
            uid=ensure_user_node(user)

            if post.is_boost:
                uid2=ensure_user_node(post.in_boost_of.author)
                pid=ensure_post_node(post.in_boost_of)
                if not G.has_edge(uid,uid2): G.add_edge(uid,uid2)
                if not G.has_edge(uid2,pid): G.add_edge(uid2,pid)
            else:
                pid=ensure_post_node(post)
                if not G.has_edge(uid,pid): G.add_edge(uid,pid)

            add_replies(post)
            return pid

        def add_replies(post):
            if post.is_reply:
                post2 = post.in_reply_to
                
                post1id = ensure_post_node(post)
                # post2id = ensure_post_node(post2)
                post2id = add_user_post(post2)

                G.add_edge(post1id, post2id)

                add_replies(post2)
            # if post.is_boost:
            #     post2 = post.in_boost_of
            #     post1id = ensure_post_node(post)
            #     post2id = add_user_post(post2)
            #     # post2id = ensure_post_node(post2)
            #     G.add_edge(post1id, post2id)

        # build
        for post in self.posts:
            add_user_post(post)

        
        return G

        
    def to_adjmat(self, g=None):
        if not g: g = self.graph()
        return pd.DataFrame(
            nx.adjacency_matrix(g).todense(),
            columns = g.nodes,
            index = g.nodes
        )

    def to_d3graph(self, g=None):
        from d3graph import d3graph
        if not g: g = self.graph()
        adjmat = self.to_adjmat(g=g)
        d3 = d3graph()
        d3.graph(adjmat)
        
        import palettable
        cmap = palettable.colorbrewer.qualitative.Dark2_7.hex_colors
        


        ntypes = [d.get('node_type','node') for n,d in g.nodes(data=True)]
        nlabels = [d.get('label','?') for n,d in g.nodes(data=True)]
        ntooltips = [d.get('tooltip','?') for n,d in g.nodes(data=True)]
        ntypes_setl = list(set(ntypes))
        
        def ntype(node):
            return g.nodes[node]['node_type']

        def sizer(node, factor=7.5):
            ntyp=ntype(node)
            if ntyp=='post':
                return 2*factor
            elif ntyp=='user':
                return 1*factor
            return .5*factor

        ncolors = [cmap[ntypes_setl.index(ntyp)] for ntyp in ntypes]
        nsizes = [sizer(n) for n in g.nodes()]


        d3.set_node_properties(
            label=nlabels,
            tooltip=ntooltips,
            color='cluster',
            size=nsizes
            # edge_color=ncolors,
            # edge_size=2

        )
        d3.set_edge_properties(directed=True)
        return d3


    def to_pyvis(self, g=None):
        from pyvis.network import Network
        if not g: g = self.graph()
        
        # expand
        for n,d in g.nodes(data=True):
            obj = d.get('obj')
            if d.get('node_type')=='user':
                g.nodes[n]['shape']='circularImage'
                g.nodes[n]['image'] = d.get('obj').avatar
                g.nodes[n]['size'] = 25
            elif d.get('node_type')=='post':
                g.nodes[n]['shape']='box'
                g.nodes[n]['label']=' '.join(w for w in obj.text.split() if w and w[0]!='@')[:40]
                
        # filter
        for n,d in g.nodes(data=True):
            for k,v in list(d.items()):
                if type(v) not in {float,int,str,dict,list}:
                    del g.nodes[n][k]
        
        # make net
        nt = Network(
            width='100%',
            height='800px',
            directed=True,
            cdn_resources = 'remote',    
            notebook=True
        )
        nt.from_nx(g)
        return nt.show('nx.html')




def parse_account_name(acct):
    un, server = '', ''
    acct = acct.strip()
    
    if acct and '@' in acct:
        if acct.startswith('@'):
            return parse_account_name(acct[1:])

        elif acct.count('@')>1:
            return parse_account_name(acct.split('/@',1)[-1])

        elif acct.startswith('http'):
            server, un = acct.split('/@')
            un = un.split('/')[0]
            server = server.split('://',1)[-1]

        elif acct.count('@')==1:
            un, server = acct.split('@',1)
            server = server.split('/')[0]

    return un,server


