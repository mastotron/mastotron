from .imports import *

def Tron():
    return Mastotron()

CACHES = {}
APIS = {}

class Mastotron():
    def __init__(self):
        global CACHES, API_SERVERS

        self._api = APIS
        self._posts = {}
        self._seen_urls = set()
        self._caches = CACHES
    
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
    
    def cache(self, dbname='cachedb'):
        if not dbname in self._caches:
            self._caches[dbname] = SqliteDict(path_db+'.'+dbname, autocommit=True)
        return self._caches.get(dbname)
    
    def status(self, url):
        if not url: return {}
        res = {}
        cache = self.cache('status')
        # with self.cache('status') as cache:
        if url in cache:
            # log.debug(f'getting {url} from cache')
            return cache[url]
        else:
            try:
                server_name = get_server_name(url)
                status_id = get_status_id(url)
                api = self.api_server(server_name)
                log.debug(f'getting {server_name}\'s {status_id} from API')
                res = api.status(status_id)
                log.debug(f'got {url} from API')
                cache[url] = res
            except Exception as e:
                print(f'!! {e}: {url} !!')
                res = {}
        return res
        
    def post(self, url_or_uri, **post_d):
        if not url_or_uri: return
        if not url_or_uri in self._posts:
            self._posts[url_or_uri] = PostModel({
                **self.status(url_or_uri), 
                **post_d,
                **{'_id':url_or_uri}
            })
        return self._posts[url_or_uri]
            

    def status_context(self, uri):
        # with self.cache('context') as cache:
        cache = self.cache('context')
        if not uri in cache:
            server,uname,status_id = get_server_account_status_id(uri)
            try:
                cache[uri] = self.api_server(server).status_context(status_id)
            except Exception as e:
                log.error(e)
                return {}
                
        return cache[uri]

    
    def latest(self, acct='', **kwargs):
        return PostList(list(self.latest_iter(**kwargs)))

    def latest_iter(self, mins_ago=60, unread_only=True):
        now = int(round(datetime.now().timestamp()))
        then = now - (mins_ago * 60)
        
        func=TronDB().since if not unread_only else TronDB().since_unread
        for post in func(then):
            post = PostModel(dict(post))
            if post.is_valid:
                yield post


    def latest_n(self, n=10):
        uris = [row['uri'] for row in self.db.all()[-n:]]
        return PostList([self.post(uri) for uri in uris])
    
    def timeline_iter(self, account_name, timeline_type='home', unread_only=True, lim=20, lim_iter=5):
        un,server=parse_account_name(account_name)
        api = self.api_user(account_name)
        try:
            timeline = api.timeline(timeline=timeline_type, local=False, remote=False)
            num_yielded = 0
            num_looped = 0
            ii=0
            while timeline:
                num_looped+=1
                if num_looped>lim_iter: break

                for post_d in timeline:
                    ii+=1
                    iduri = f"https://{server}/@{post_d.get('account').get('acct')}/{post_d.get('id')}"
                    if iduri:
                        post = self.post(iduri, **dict(post_d))
                        if post: 
                            if not unread_only or not post.is_read:
                                print(f'{ii:04} {post} {"is" if post.is_read else "is not"} read and it {"is" if post.is_boost else "is not"} a boost post')
                                yield post
                                num_yielded+=1
                                if lim and num_yielded>=lim: 
                                    timeline = None
                                    break
                # keep going
                if timeline is None: break
                try:
                    timeline = api.fetch_next(timeline)
                except MastodonNetworkError as e:
                    log.error(e)
                    print(e)
                    api = self.api_user(account_name)
                    try:
                        timeline = api.fetch_next(timeline)
                    except MastodonNetworkError as e:
                        print(e)
                        timeline = None
        except MastodonNetworkError as e:
            print(e)
            log.error(e)
            pass

        # print(num_looped, num_yielded, timeline)
                


    def timeline(self, account_name, lim=LIM_TIMELINE, **y):
        iterr = self.timeline_iter(account_name, lim=lim, **y)
        # res = list(islice(iterr, n))
        return PostList(iterr)
    
