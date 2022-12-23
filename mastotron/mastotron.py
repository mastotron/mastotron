import os,sys; sys.path.insert(0,'..')
from mastodon import Mastodon
from datetime import datetime, timedelta, timezone
from scipy.stats import gmean
from math import sqrt
from pprint import pprint
import pandas as pd
from IPython.display import Markdown, display
def printm(x): display(Markdown(x))
import webbrowser,json


path_data = os.path.expanduser('~/.mastotron')
path_client_secret = os.path.join(path_data, 'clientcred.secret')
path_user_secret = os.path.join(path_data, 'usercred.secret')
path_env = os.path.join(path_data, 'config.json')



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
    

    def iter_timeline(self, timeline_type='home', hours_ago=24, max_posts=1000):
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
                post_is_boost = post['reblog'] is not None
                if post_is_boost: post = post['reblog']
                post['is_boost'] = post_is_boost
                post['is_reply'] = post['in_reply_to_id'] is not None

                if post.url not in seen_post_urls:
                    seen_post_urls.add(post.url)

                    scored = post['scores'] = score_post(post)
                    for k,v in scored.items(): post['score_'+k]=v
                    yield post

            # keep going
            timeline = self.api.fetch_previous(timeline)

    def timeline(self, **kwargs):
        odf = pd.DataFrame(self.iter_timeline(**kwargs))
        odf = odf.sort_values('score_All', ascending=False)
        return odf




def score_post(post):
    """
    These scoring ideas come from mastodon_digest (https://github.com/hodgesmr/mastodon_digest).
    """

    scores={}
    
    # simple score
    scores['Simple'] = gmean([
        post['reblogs_count']+1, 
        post['favourites_count']+1,
    ])
    # simple score
    scores['ExtendedSimple'] = gmean([
        post['reblogs_count']+1, 
        post['favourites_count']+1,
        post['replies_count'] + 1
    ])

    # add weighted versions
    for score_name in list(scores.keys()):
        scores[score_name+'Weighted'] = scores[score_name] / sqrt(post.get('account',{}).get("followers_count",0)+1)

    scores['All'] = gmean(list(scores.values()))
    return scores
    

