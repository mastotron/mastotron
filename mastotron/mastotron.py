from .imports import *


class Mastotron():
    def __init__(self):
        self._api = {}
    
    def _get_path_api_auth(self, server):
        return os.path.join(
            path_data, 
            'mastodon_clients',
            get_server_name(server)+'.secret'
        )
    def _get_path_user(self, account_name):
        un,server = parse_account_name(account_name)
        return os.path.join(
            path_data,
            f'{un}@{server}'
        )
        
    def _get_path_user_auth(self, account_name):
        return os.path.join(
            self._get_path_user(account_name),
            f'usercred.secret'
        )

    def api(self, server):
        server = get_server_name(server)
        path_client_secret = self._get_path_api_auth(server)

        if not server in self._api:
            odir=os.path.dirname(path_client_secret)
            if not os.path.exists(odir): os.makedirs(odir)
            
            Mastodon.create_app(
                f'mastotron_{server.replace(".","")}',
                api_base_url = f'https://{server}/',
                to_file = path_client_secret
            )

            self._api[server] = Mastodon(client_id = path_client_secret)
        return self._api[server]

    
    def user(self, account_name, code=None):
        un,server = parse_account_name(account_name)
        path_user_secret = self._get_path_user_auth(account_name)
        if not os.path.exists(path_user_secret):
            odir = os.path.dirname(self.path_user_secret)
            if not os.path.exists(odir): os.makedirs(odir)
            
            api = self.api(server)
        
            if not code:
                url=api.auth_request_url()
                webbrowser.open(url)
                code = input('Paste the code from the browser:\n')
            
            api.log_in(code = code, to_file = path_user_secret)
            return api
        else:
            return Mastodon(access_token = path_user_secret)

    
    @cached_property
    def db(self):
        from sqlitedict import SqliteDict
        return SqliteDict(path_db, autocommit=True)
    
    def status(self, url, **post_d):
        if not url in self.db:
            if not post_d:
                server_name = get_server_name(url)
                status_id = get_status_id(url)
                #post_d=self.api(server_name).status(status_id)
                post_d = mastodon_post_d
            self.db[url] = post_d
        else:
            post_d = self.db.get(url)
        return post_d

    def post(self, url, as_dict=False, **post_d):
        post_d = self.status(url, **post_d)
        if as_dict: return post_d
        return PostModel(post_d)
    

    def timeline(self, account_name, max_posts=20, hours_ago=1,timeline_type='home'):
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
            for post_d in timeline:
                total_posts_seen += 1

                if post_d.url not in seen_post_urls:
                    seen_post_urls.add(post_d.url)
                    yield self.post(post_d.url, **post_d)

            # keep going
            timeline = self.api.fetch_previous(timeline)

    def latest_post(self, **kwargs):
        iterr=self.timeline(**kwargs)
        return next(iterr)
    latest = latest_post

    def latest_posts(self, max_posts=20, **kwargs):
        iterr=self.iter_timeline(
            max_posts=max_posts, 
            **kwargs
        )
        return PostList(iterr)

    

        









# class UserMastotron():
#     def __init__(self, account_name, code=None):
        
#         # get un and server from acct name
#         self.username,self.servername = parse_account_name(account_name)
#         self.code=code
#         if not self.username or not self.servername:
#             raise Exception('! Invalid account name !')

#         set_api(self)

#     @property
#     def acct(self):
#         return self.username+'@'+self.servername
#     @property
#     def acct_safe(self):
#         return self.username+'__at__'+self.servername
    
#     @property
#     def server(self):
#         return f'https://{self.servername}'

#     @property
#     def path_client_secret(self):
#         return os.path.join(
#             self.path_acct,
#             f'clientcred.secret'
#         )

#     @property
#     def path_acct(self):
#         return os.path.join(
#             path_data,
#             self.acct
#         )

#     @property
#     def path_user_secret(self):
#         return os.path.join(
#             self.path_acct,
#             f'usercred.secret'
#         )
    
#     @property
#     def path_graphdb(self):
#         return os.path.join(
#             self.path_acct,
#             f'graph.db'
#         )
    

#     @property
#     def api(self):
#         if not hasattr(self,'_api'):
#             # make sure app token exists
#             self.init_app()

#             # make sure user token exists
#             self.init_user()

#             # log in and set app
#             self._api = Mastodon(access_token = self.path_user_secret)

#         return self._api

#     def init_app(self):
#         if not os.path.exists(self.path_client_secret):
#             if not os.path.exists(os.path.dirname(self.path_client_secret)):
#                 os.makedirs(os.path.dirname(self.path_client_secret))
#             Mastodon.create_app(
#                 app_name,
#                 api_base_url = self.server,
#                 to_file = self.path_client_secret
#             )

#     def auth_request_url(self):
#         self.init_app()
#         api = Mastodon(client_id = self.path_client_secret)
#         url=api.auth_request_url()
#         return url

#     def user_is_init(self):
#         self.init_app()
#         return os.path.exists(self.path_user_secret)

#     def init_user(self, code=None):
#         if code is None: code=self.code
#         if not self.user_is_init():
#             if not os.path.exists(os.path.dirname(self.path_user_secret)):
#                 os.makedirs(os.path.dirname(self.path_user_secret))
            
#             if not os.path.exists(self.path_client_secret):
#                 self.init_app()

#             api = Mastodon(client_id = self.path_client_secret)
#             if not code:
#                 url=api.auth_request_url()
#                 webbrowser.open(url)
#                 code = input('Paste the code from the browser:\n')
            
#             api.log_in(code = code, to_file = self.path_user_secret)

#     def iter_timeline(self, max_posts=20, hours_ago=1,timeline_type='home'):
#         # init vars
#         total_posts_seen = 0
#         # filters = self.api.filters()
#         seen_post_urls = set()

#         # Set our start query
#         start = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
#         # get initial response
#         timeline = self.api.timeline(timeline=timeline_type, min_id=start)
#         # get filters
#         while timeline and total_posts_seen < max_posts:
#             # if filters: 
#                 # timeline = self.api.filters_apply(timeline, filters, "home")
#             for post in timeline:
#                 total_posts_seen += 1

#                 if post.url not in seen_post_urls:
#                     seen_post_urls.add(post.url)

#                     # yield Post(post, _tron=self)
#                     yield post

#             # keep going
#             timeline = self.api.fetch_previous(timeline)

#     def latest_post(self, **kwargs):
#         iterr=self.iter_timeline(**kwargs)
#         return next(iterr)
#     latest = latest_post

#     def latest_posts(self, max_posts=20, **kwargs):
#         iterr=self.iter_timeline(
#             max_posts=max_posts, 
#             **kwargs
#         )
#         return PostList(iterr)

#     def timeline(self, **kwargs):
#         return PostList(self.iter_timeline(**kwargs))

#     # def get_post(self, id):
#         # return Post(self.api.status(id), _tron=self)
    

#     @cached_property
#     def gdb(self):
#         return GraphDB(self)

#     @cached_property
#     def db(self):
#         return TronDB()


#     # def ingest_post(self):
#     #     with self as sess:
#     #         poster = dbPoster(**poster_d)
#     #         post = dbPost(**post_d)
#     #         c.add(poster)
#     #         c.add(post)
#     #         c.commit()
#     #         c.refresh(poster)
#     #         c.refresh(post)
#     #         print(post.uri, post.poster.uri)
#     #         x=c.exec(select(dbPost)).one()
#     #         print(post.poster.posts)


#     def get_post(self, uri):
#         pass





