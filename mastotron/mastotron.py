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
path_client_secret = os.path.join(path_data, 'clientcred.secret')
path_user_secret = os.path.join(path_data, 'usercred.secret')
path_env = os.path.join(path_data, 'config.json')

API = None
def get_api():
    global API
    if API is None:
        API = Mastotron()
    return API
def set_api(mastotron_obj):
    global API
    API = mastotron_obj

class Mastotron():
    def __init__(self):
        # make sure app token exists
        if not os.path.exists(path_client_secret): 
            self.create_app()
        # make sure user token exists
        if not os.path.exists(path_user_secret):
            self.api = Mastodon(client_id = path_client_secret)
            self.log_in()
        # log in and set app
        self.api = Mastodon(access_token = path_user_secret)

    def env(self):
        if not os.path.exists(path_env):
            envd = {
                'MASTODON_BASE_URL':input('What is the base URL for your server?\n'),
            }
            if not os.path.exists(os.path.dirname(path_env)):
                os.makedirs(os.path.dirname(path_env))
            with open(path_env,'w') as of:
                json.dump(envd, of)
        else:
            with open(path_env) as f:
                envd = json.load(f)
        
        return envd


    def create_app(self):
        Mastodon.create_app(
            'mastotron',
            api_base_url = self.env().get('MASTODON_BASE_URL'),
            to_file = path_client_secret
        )

    def log_in(self):
        url=self.api.auth_request_url()
        webbrowser.open(url)
        code = input('Paste the code from the browser:\n')
        self.api.log_in(code = code, to_file = path_user_secret)
    

    def iter_timeline(self, timeline_type='home', hours_ago=1, max_posts=100):
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
                # post_is_boost = post['reblog'] is not None
                # if post_is_boost: post = post['reblog']
                # post['is_boost'] = post_is_boost
                # post['is_reply'] = post['in_reply_to_id'] is not None

                if post.url not in seen_post_urls:
                    seen_post_urls.add(post.url)

                    yield Post(post)

            # keep going
            timeline = self.api.fetch_previous(timeline)

    def latest_post(self, **kwargs):
        iterr=self.iter_timeline(**kwargs)
        return next(iterr)

    def latest_posts(self, max_posts=20, hours_ago=24*7, **kwargs):
        iterr=self.iter_timeline(
            max_posts=max_posts, 
            hours_ago=hours_ago, 
            **kwargs
        )
        return list(iterr)

    def timeline(self, **kwargs):
        return list(self.iter_timeline(**kwargs))

    def timeline_df(self, timeline=None, sort_by_score = False, **kwargs):
        if timeline is None: timeline = self.iter_timeline(**kwargs)
        
        odf = pd.DataFrame(timeline)
        
        if sort_by_score: 
            odf = odf.sort_values('score_All', ascending=False)
        return odf





class Post(AttribAccessDict):

    def __init__(self,*args,id=None,**kwargs):
        ## init self
        if id is not None:
            if not kwargs:
                kwargs = get_api().api.status(id)
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
        
                

    def __repr__(self): return f'Post(id={self.id})'
    def _repr_html_(self): 
        if self.is_boost:
            o = f'''
                <div class="post reblog" style="border:1px solid blue; padding: 0 1em;">
                    <p>
                        {self.author._repr_html_()} reposted at {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.in_boost_of._repr_html_()}
                    <br/>

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

                    {"<p><b><i>... in reply to:</i></b></p> " + self.in_reply_to._repr_html_() + " <br/> " if self.is_reply else ""}
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


