from .imports import *


def Post(url, as_dict=False, **post_d):
    tron=get_tron()
    return tron.post(url, as_dict=as_dict, **post_d)

class PostModel(AttribAccessDict):    

    def data(self):
        return dict(
            uri=self.uri,
            poster_uri=self.author.uri,
            url_local=self.get_url_local(),
            text=self.text,
            html=self.html,
            is_boost=self.is_boost,
            is_reply=self.is_reply,
            in_boost_of__uri=self.in_boost_of.uri if self.in_boost_of else '',
            in_reply_to__uri=self.in_reply_to.uri if self.in_reply_to else '',
            timestamp=self.timestamp,
            
            **{f'score_{k}':v for k,v in self.scores().items()}
        )

    @property
    def timestamp(self):
        return int(round(self.created_at.timestamp()))
        
    @cached_property
    def post_id(self):
        return os.path.join(self.poster_id, self.url.split('/')[-1])
    @cached_property
    def poster_id(self):
        return self.author.account
        
    @cached_property
    def in_boost_of(self):
        return Post(self['reblog'], _tron=self._tron) if self['reblog'] else None

    
    @cached_property
    def in_reply_to(self):
        return Post(id=self['in_reply_to_id'], _tron=self._tron) if self['in_reply_to_id'] else None
        
    @property
    def url_or_uri(self):
        return self.url if self.url else self.uri
    

                

    def __repr__(self): return f"Post('{self.url_or_uri}')"

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
        from .poster import Poster
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

    @property
    def text(self):
        return unhtml(self.content).strip()

    @property
    def label(self, limsize=40):
        stext = self.spoiler_text
        if not stext: stext=' '.join(w for w in self.text.split() if w and w[0]!='@')
        return stext[:limsize]
