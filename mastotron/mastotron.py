from .imports import *


def Tron():
    return Mastotron()

class Mastotron():
    def __init__(self):
        self._api = {}
        self._posts = {}
        self._seen_urls = set()
    
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

    def api(self, server_or_account):
        return self.api_server(server_or_account) if not '@' in server_or_account else self.api_user(server_or_account)

    def api_server(self, server):
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

    
    def user_is_init(self, account_name):
        path_user_secret = self._get_path_user_auth(account_name)
        return os.path.exists(path_user_secret)

    def api_user(self, account_name, code=None):
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
        return TinyDB(path_tinydb)
    
    @cached_property
    def cache(self):
        return SqliteDict(path_db, autocommit=True)
    
    def status(self, url):
        res = {}
        with self.cache as cache:
            if url in cache:
                return cache[url]
            else:
                server_name = get_server_name(url)
                status_id = get_status_id(url)
                api = self.api_server(server_name)
                try:
                    res = api.status(status_id)
                    # except MastodonNotFoundError as e:
                    try:
                        cache[url] = res
                    except AttributeError:
                        pass
                except Exception as e:
                    print(f'!! {e}: {url} !!')
                    res = {}

        return res
        

    def post(self, url='', **post_d):
        if not url: return
        # print(f'post! url = {url}; keys = {post_d.keys()}')
        if not url in self._posts:
            post_d = self.status(url) if not post_d else post_d
            self._posts[url] = PostModel({'url':url, **post_d}) if post_d else None
        
        return self._posts[url]
            
    
    def latest(self, mins_ago=60):
        now = int(round(datetime.now().timestamp()))
        then = now - (mins_ago * 60)

        res = self.db.search(
            Query().timestamp.test(
                lambda timestamp: type(timestamp) is int and timestamp>=then
            )
        )
        return PostList([self.post(row['uri']) for row in res])


    def latest_n(self, n=10):
        uris = [row['uri'] for row in self.db.all()[-n:]]
        return PostList([self.post(uri) for uri in uris])
    
    def timeline_iter(self, account_name, timeline_type='home'):
        api = self.api_user(account_name)
        timeline = api.timeline(timeline=timeline_type)
        seen_urls = self._seen_urls
        while timeline:
            for post_d in timeline:
                if post_d.url not in seen_urls:
                    seen_urls.add(post_d.url)
                    post = self.post(**dict(post_d))
                    if post:
                        yield post
            # keep going
            timeline = api.fetch_previous(timeline)


    def timeline(self, account_name, n=10, **y):
        iterr = self.timeline_iter(account_name, **y)
        res = list(islice(iterr, n))
        return PostList(res)
    

        




