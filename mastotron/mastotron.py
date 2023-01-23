from .imports import *
NUM_GOT_CONTEXTS=0
NUM_GOT_STATUS=0

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
            odir = os.path.dirname(path_user_secret)
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
    
    def status(self, url_or_uri, **post_d):
        global NUM_GOT_STATUS

        res = {}
        url = url_or_uri
        if url:
            cache = self.cache('status')
            if post_d:
                cache[url]={**cache.get(url,{}), **post_d}
                res = cache[url]
            elif url in cache:
                res = cache[url]
            else:
                NUM_GOT_STATUS+=1
                # if NUM_GOT_STATUS>1: STOPXX

                try:
                    server_name = get_server_name(url)
                    status_id = get_status_id(url)
                    api = self.api_server(server_name)

                    print(f'getting {server_name}\'s {status_id} from API')
                    res = api.status(status_id)
                    log.debug(f'got {url} from API')
                    cache[url] = res
                except Exception as e:
                    print(f'!! {e}: {url} !!')
        return res
        
    def post(self, url_or_uri, **post_d):
        if not url_or_uri: return
        if not url_or_uri in self._posts:
            self._posts[url_or_uri] = PostModel({
                **self.status(url_or_uri, **post_d),
                **{'_id':url_or_uri}
            })
        return self._posts[url_or_uri]
            

    def status_context(self, uri, **status_d):
        global NUM_GOT_CONTEXTS
        # with self.cache('context') as cache:
        cache = self.cache('context')
        if status_d:
            # cache[uri] = {**cache.get(uri,{}), **status_d}
            cache[uri] = status_d
        else:
            if not uri in cache:
                server,uname,status_id = get_server_account_status_id(uri)
                # print(server,uname,status_id)
                NUM_GOT_CONTEXTS+=1
                # if NUM_GOT_CONTEXTS>1: STOPXXX
                try:
                    print(f'getting {server}\'s CONTEXT {status_id} from API')
                    statd=self.api_server(server).status_context(status_id)
                    cache[uri] = statd

                    post = Post(uri)
                    l_pre=[Post(**d) for d in statd.get('ancestors',[])]
                    l_post=[Post(**d) for d in statd.get('descendants',[])]
                    # print('post:',post)
                    # pprint(l_pre)
                    # pprint(l_post)
                    
                    if l_pre:
                        l_preself=l_pre+[post]
                        for i in range(len(l_preself)-1):
                            a=l_preself[i]
                            b=l_preself[i+1]
                            if b.is_reply and not b.out(REL_IS_REPLY_TO):
                                # print(f'{a} --> {b} ???')
                                b.relate(a,REL_IS_REPLY_TO)
                    
                    if l_post:
                        a=post
                        for b in l_post:
                            if b.is_reply and not b.out(REL_IS_REPLY_TO):
                                # print(f'{a} --> {b} ???')
                                b.relate(a,REL_IS_REPLY_TO)
                    
                except Exception as e:
                    log.error(e)
                    print(f'!! {e} !!')
                    return {}
        return cache[uri]

    
    def latest(self, acct='', lim=LIM_TIMELINE, **kwargs):
        iterr = self.iter_latest(acct=acct, lim=lim, **kwargs)
        return PostList(iterr, lim=lim)

    def iter_latest(
            self,
            acct='', 
            unread_only=True, 
            lim=LIM_TIMELINE, 
            follow_chains=True, 
            **kwargs):
            
        def iter_posts():
            if acct: yield from self.iter_timeline(acct, unread_only=unread_only, lim=lim, **kwargs)
            yield from self.database_iter(**kwargs)

        def iter_posts_filtered():
            seen=set()
            for post in iter_posts():
                if not post in seen:
                    seen.add(post)
                    if unread_only and post.is_read: continue
                    yield post
        
        seen=set()
        for post in iter_posts_filtered():
            yield post
            seen.add(post)
        
        # if follow_chains:
        #     for post in seen:
        #         yield from post.iter_context(lim=lim)


    def database_iter(self,timestamp=None,**kwargs):
        seen=set()
        # iterr=tqdm(
        #     list(iter_graphtimes(timestamp)),
        #     desc=f'Querying every {GRAPHTIME_ROUNDBY} mins'
        # )
        iterr=iter_graphtimes(timestamp)
        for timestr in iterr:
            rels = TronDB().get_rels_inc(timestr, REL_GRAPHTIME)
            for id in rels:
                post=Post(id).source
                if post not in seen:
                    seen.add(post)
                    yield post                

    def iter_timeline(
            self,
            account_name, 
            timeline_type='home', 
            unread_only=True, 
            lim=LIM_TIMELINE, 
            lim_iter=5, 
            as_source=True,
            **kwargs):
        
        un,server=parse_account_name(account_name)
        api = self.api_user(account_name)
        seen=set()
        try:
            print('calling timeline now')
            timeline = api.timeline(timeline=timeline_type, local=False, remote=False)
            num_yielded = 0
            num_looped = 0
            ii=0
            # pbar = tqdm(total=lim)
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
                                log.debug(f'{ii:04} {post} {"is" if post.is_read else "is not"} read and it {"is" if post.is_boost else "is not"} a boost post')
                                opost = post.source if as_source else post
                                if not opost in seen:
                                    # pbar.update()
                                    yield opost
                                    seen.add(opost)
                                    num_yielded+=1
                                    if lim and num_yielded>=lim: 
                                        timeline = None
                                        # pbar.close()
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
        
        pbar.close()

        # print(num_looped, num_yielded, timeline)
                


    def timeline(self, account_name, lim=LIM_TIMELINE, **y):
        iterr = self.iter_timeline(account_name, lim=lim, **y)
        return PostList(iterr, lim=lim)
    


    