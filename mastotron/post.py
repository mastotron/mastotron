from .imports import *


def Post(url, **post_d):
    tron=get_tron()
    return tron.post(url, **post_d)

class PostModel(DictModel):
    def __init__(self,*x,**y):
        super().__init__(*x,**y)
        self.save()

    @property
    def uri(self):
        return self._data.get('url')

    def is_valid(self):
        return bool(self.uri)

    @property
    def author(self):
        from .poster import Poster
        return Poster(self.account)

    # def get_url_local(self, server):
        # return '/'.join([server,'@'+self.acct])


    
    @property
    def timestamp(self):
        return int(round(self.datetime.timestamp()))

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
    def poster_id(self):
        return self.author.account
        
    @cached_property
    def in_boost_of(self):
        return PostModel(self.reblog) if self.reblog else None

    @cached_property
    def in_reply_to(self):
        if self.in_reply_to_uri:
            return Post(self.in_reply_to_uri)

    @cached_property
    def in_reply_to_uri(self, key = 'in_reply_to_uri'):
        if not self.in_reply_to_id: return
        if not key in self._data:
            oldurl = f'{os.path.dirname(self.url)}/{self.in_reply_to_id}'
            newurl = requests.get(oldurl).url
            self.store(key, newurl)
        return self._data[key]

    @property
    def url_or_uri(self):
        return self.url if self.url else self.uri
    
    def __repr__(self): return f"Post('{self.uri}')"

    @property
    def html(self):
        return self._repr_html_(allow_embedded=False)

    def _repr_html_(self, allow_embedded = True): 
        if self.is_boost:
            o = f'''
                <div class="post reblog">
                    <p>
                        {self.author._repr_html_()} reposted at {self.created_at.strftime("%m/%d/%Y at %H:%M:%S")}:
                    </p>
                    
                    {self.in_boost_of._repr_html_()}
                    <p>Post ID: <a href="{self.url}" target="_blank">{self.id}</a></p>

                </div>
            '''
        else:
            imgs_urls = [d.get('preview_url') for d in self.media_attachments] if self.media_attachments else []
            imgs = [
                f'<a href="{url}" target="_blank"><img src="{url}" /></a>'
                for url in imgs_urls
                if url
            ]

            o = f'''
                <div class="post origpost">
                    <p>
                        {self.author._repr_html_()} posted on {self.datetime_str}:
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
                        Post ID: <a href="{self.url}" target="_blank">{self.id}</a>
                    </p>

                    {"<p><i>... in reply to:</i></p> " + self.in_reply_to._repr_html_() + " <br/> " if allow_embedded and self.is_reply else ""}
                </div>
            '''
            
        return '\n'.join([ln.lstrip() for ln in o.split('\n')]).strip()

    
    
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


    def scores(self):
        """
        These scoring ideas come from mastodon_digest (https://github.com/hodgesmr/mastodon_digest).
        """
        if not self._scores:
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
    def db(self):
        if not self._db: self._db = get_tron().db
        return self._db
    
    @property
    def cache(self):
        if not self._cache: self._cache = get_tron().cache
        return self._cache

    def store(self, key, val):
        self._data[key] = val
        with self.cache as cache:
            if not self.uri in cache: cache[self.uri] = {}
            cache[self.uri] = {**cache[self.uri], **{key:val}}



    def data_tosave(self):
        return dict(
            uri=self.uri,
            poster_uri=self.author.uri,
            # text=self.text,
            # html=self.html,
            is_boost=self.is_boost,
            is_reply=self.is_reply,
            in_boost_of_uri=self.in_boost_of.uri if self.in_boost_of else '',
            in_reply_to_uri=self.in_reply_to_uri if self.in_reply_to else '',
            timestamp=self.timestamp,
            **{f'score_{k}':v for k,v in self.scores().items()}
        )

    def save(self):
        if self.is_valid() and not self._saved:
            try:
                self.db.upsert(self.data_tosave(), Query().uri == self.uri)
                self._saved = True
            except json.decoder.JSONDecodeError as e:
                print(f'JSON error?: {e}')
        return self
        
    def data_saved(self):
        res=self.db.search(Query().uri == self.uri)
        return res[0] if res else {}

    @cached_property
    def node_data(self):
        odx={}
        odx['html'] = self._repr_html_(allow_embedded=False)
        odx['shape']='box'
        odx['label']=self.label
        odx['text'] = self.text
        odx['node_type']='post'
        odx['color'] = '#1f465c' if not self.is_reply else '#061f2e'
        return odx


