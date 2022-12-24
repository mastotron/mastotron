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
    def __init__(self, account_name):
        
        # get un and server from acct name
        self.username, self.servername = parse_account_name(account_name)

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

    def init_user(self):
        if not os.path.exists(self.path_user_secret):
            if not os.path.exists(os.path.dirname(self.path_user_secret)):
                os.makedirs(os.path.dirname(self.path_user_secret))
            
            if not os.path.exists(self.path_client_secret):
                self.init_app()

            api = Mastodon(client_id = self.path_client_secret)
            url=api.auth_request_url()
            webbrowser.open(url)
            code = input('Paste the code from the browser:\n')
            api.log_in(code = code, to_file = self.path_user_secret)

    def iter_timeline(self, max_posts=100, hours_ago=24*7, timeline_type='home'):
        # init vars
        total_posts_seen = 0
        filters = self.api.filters()
        seen_post_urls = set()

        # Set our start query
        start = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        # get initial response
        timeline = self.api.timeline(timeline=timeline_type, min_id=start)
        # get filters
        while timeline and total_posts_seen < max_posts:
            if filters: 
                timeline = self.api.filters_apply(timeline, filters, "home")
            for post in timeline:
                total_posts_seen += 1

                if post.url not in seen_post_urls:
                    seen_post_urls.add(post.url)

                    yield Post(post)

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
        return Post(self.api.status(id))
    get = get_post
    
    def Post(self, id=None, **kwargs):
        return Post(_tron=self, id=id, **kwargs)




class Post(AttribAccessDict):

    def __init__(self,*args,id=None,_tron=None,**kwargs):
        ## init self
        if id is not None:
            if not kwargs:
                kwargs = (get_api() if not _tron else _tron).api.status(id)
            else:
                kwargs['id'] = id
        
        ## pass into dict init
        super().__init__(*args, **kwargs)

        
        
    @property
    def in_boost_of(self):
        if not hasattr(self,'_post_reposted'):
            self._post_reposted = Post(self['reblog']) if self['reblog'] else None
        return self._post_reposted

    
    @property
    def in_reply_to(self):
        if not hasattr(self,'_post_repliedto'):
            self._post_repliedto = Post(id=self['in_reply_to_id']) if self['in_reply_to_id'] else None
        return self._post_repliedto
        
                

    def __repr__(self): return f'tron.Post({self.id})'
    def _repr_html_(self): 
        if self.is_boost:
            o = f'''
                <div class="post reblog" style="border:1px solid blue; padding: 0 1em;">
                    <p>
                        {self.author._repr_html_()} reposted at {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.in_boost_of._repr_html_()}
                    <p>Post ID: {self.id}</p>

                </div>
            '''
        else:
            imgs_urls = [d.get('preview_url') for d in self.media_attachments]
            imgs = [
                f'<a href="{url}"><img src="{url}" /></a>'
                for url in imgs_urls
                if url
            ]

            o = f'''
                <div class="post origpost" style="border:1px solid orange;padding:0 1em;">
                    <p>
                        {self.author._repr_html_()} <a href="{self.url}">wrote</a> on {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.content}

                    <center>{"    ".join(imgs)}</center>
                    
                    <p>
                        {self.replies_count:,} 🗣
                        &nbsp; | &nbsp; 
                        {self.reblogs_count:,} 🔁
                        &nbsp; | &nbsp;
                        {self.favourites_count:,} 💙
                        &nbsp; | &nbsp;
                        Post ID: {self.id}
                    </p>

                    {"<p><i>... in reply to:</i></p> " + self.in_reply_to._repr_html_() + " <br/> " if self.is_reply else ""}
                </div>
            '''
            
        return '\n'.join([ln.lstrip() for ln in o.split('\n')])

    @property
    def author(self):
        return Poster(self.get('account',{}))

    
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
        



class Poster(AttribAccessDict):
    def _repr_html_(self):
        return f'<a href="{self.url}">{self.acct}</a> ({self.followers_count:,} 👥)'


    @property
    def num_followers(self):
        return self.followers_count

    @property
    def num_following(self):
        return self.following_count





from collections import UserList

class PostList(UserList):
    def __init__(self, l):
        super().__init__(l)
    
    def sort_chron(self):
        self.sort(key=lambda post: post.created_at, reverse=True)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)








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