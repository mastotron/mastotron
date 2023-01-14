from .imports import *

def to_html(x, **y):
    from .post import PostModel
    if isinstance(x, PostModel):
        return post_to_html(x, **y)
    else:
        return ''

def post_to_html(self, allow_embedded = True, **y): 
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