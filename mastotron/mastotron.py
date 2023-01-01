from .imports import *



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
            self.path_acct,
            f'clientcred.secret'
        )

    @property
    def path_acct(self):
        return os.path.join(
            path_data,
            self.acct
        )

    @property
    def path_user_secret(self):
        return os.path.join(
            self.path_acct,
            f'usercred.secret'
        )
    
    @property
    def path_graphdb(self):
        return os.path.join(
            self.path_acct,
            f'graph.db'
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
    

    @cached_property
    def gdb(self):
        return GraphDB(self)
