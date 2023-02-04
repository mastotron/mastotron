from .imports import *


svg_str_htmlkey='[[HTML]]'
# svg_str=f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect x="0" y="0" width="100%" height="100%" fill="#7890A7" stroke-width="5" stroke="#ffffff" ></rect><foreignObject x="1" y="1" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:40px">{svg_str_htmlkey}</div></foreignObject></svg>'''
svg_str=f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><foreignObject x="1" y="1" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:4em">{svg_str_htmlkey}</div></foreignObject></svg>'''


def get_svg_url(svg_str):
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg_str)

def html2svg(html):
    return get_svg_url(svg_str.replace(svg_str_htmlkey, html))




def to_html(x, **y):
    from .post import PostModel
    if isinstance(x, PostModel):
        return post_to_html(x, **y)
    else:
        return ''

#                 <p>Post ID: <a href="{self._id}" target="_blank">{self.id}</a></p>


def post_to_html(self, allow_embedded = True, url=None, local_server='', **y): 
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
        if self.is_boost and self.is_boost_of:
            embed_str = post_to_html(self.is_boost_of)
        elif self.is_reply and self.is_reply_to:
            embed_str = post_to_html(self.is_reply_to)
    
    # header
    hdrstr=f'<div class="post_author">{austr}</div>'
    uristr=f''
    # stats
    url = self.url if self.url else self.uri
    localurl = f'https://{local_server}/authorize_interaction?uri={url}' if local_server else url
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
            <span class="post_uristr">Posted <a href="{localurl}" target="_blank">{self.datetime_str_h}</a></span>
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



def post_to_svg(self): 
    svg_str_pre='<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400"><rect x="0" y="0" width="100%" height="100%" fill="#dddddd"/><foreignObject x="0" y="0" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:100px">'
    svg_str_post='</div></foreignObject></svg>'

    datestr=f'<a href="{self._id}" target="_blank">{self.datetime_str_h}</a>'
    austr=f'{self.author.display_name} ({self.author.followers_count:,} 👥)'

    ohtml = f'''
        <div class="postsvg">
            {austr}
            {datestr}
            {self.content}
        </div>
    '''
    osvg_str = svg_str_pre + ohtml + svg_str_post
    return get_svg_url(osvg_str)