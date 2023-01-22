from .imports import *

def to_html(x, **y):
    from .post import PostModel
    if isinstance(x, PostModel):
        return post_to_html(x, **y)
    else:
        return ''

#                 <p>Post ID: <a href="{self._id}" target="_blank">{self.id}</a></p>
def post_to_html(self, allow_embedded = True, url=None, **y): 
    datestr=f'<a href="{self._id}" target="_blank">{self.datetime_str_h}</a>'
    austr=f'<img class="post_avatarimg" src="{self.author.avatar}" width="50px" height="50px" /><a href="{self._id}" target="_blank">{self.author.display_name}</a> ({self.author.followers_count:,} 👥)'
    imgs_urls = [d.get('preview_url') for d in self.media_attachments] if self.media_attachments else []
    imgs_str = "    ".join([
        f'<a href="{xurl}" target="_blank"><img class="post_postimg" src="{xurl}" /></a>'
        for xurl in imgs_urls
        if xurl
    ])
    imgs_str=f'<center>{imgs_str}</center>' if imgs_str else ''

    # class string
    classes = ['post']
    if self.is_boost: classes.append('reblog')
    if self.is_reply: classes.append('reply')
    class_str = ' '.join(classes)

    # embed
    embed_str = ''
    if allow_embedded:
        if self.is_boost and self.in_boost_of:
            embed_str = post_to_html(self.in_boost_of)
        elif self.is_reply and self.in_reply_to:
            embed_str = post_to_html(self.in_reply_to)
    
    # header
    hdrstr=f'<div class="post_author">{austr}</div>'
    uristr=f''
    # stats
    url = self.url if self.url else self.uri
    stats_str = f'''
        <div class="post_stats">
            {self.replies_count:,} 🗣
            |
            {self.reblogs_count:,} 🔁
            |
            {self.favourites_count:,} 💙
            |
            <span class="post_uristr"><a href="{self.urli}" target="_blank">URI</a></span>
            |
            Read: {self.is_read}
            |
            <span class="post_uristr"><a href="{self._id}" target="_blank">Posted {self.datetime_str_h}</a></span>
        </div>
    ''' if not self.is_boost else f'''
        <div class="post_stats">
            <span class="post_uristr">Reposted <a href="{url}" target="_blank">{self.datetime_str_h}</a></span>
        </div>
    '''

    ohtml = f'''
        <div class="{class_str}">
            {hdrstr}
            {self.content}
            {imgs_str}
            {embed_str}
            {stats_str}
        </div>
    '''
    ohtml = '\n'.join([ln.lstrip() for ln in ohtml.split('\n')]).strip()
    return ohtml