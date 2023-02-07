from .imports import *


class Poster(DictModel):

    @property
    def account(self):
        un, server = parse_account_name(self.url)
        return f'{un}@{server}'

    @property
    def is_valid(self):
        return bool(self.uri)

    @property
    def data(self):
        return dict(
            uri=self.uri,
            account=self.account,
            name=self.display_name,
            url_local=self.url_local,
            text=self.text,
            html=self.html,
            num_followers=self.num_followers,
            num_following=self.num_following,
            is_bot=self.bot,
            is_org=self.group,
            timestamp=self.timestamp,
        )

    @property
    def timestamp(self):
        return int(round(self.created_at.timestamp()))
    
    def __hash__(self):
        return hash(self.acct)
    
    def __eq__(self, other):
        return self._id == other._id

    def __repr__(self):
        return f'Poster({self._id})'

    @cached_property
    def html(self): return self._repr_html_(allow_embedded=True)

    @cached_property
    def text(self): return unhtml(self.note).strip() if self.note else ''

    def _repr_html_(self, allow_embedded=False, **kwargs):
        return f'<span class="author"><img src="{self.avatar}" width="50" height="50" /> <a href="{self._id}" target="_blank">{self.display_name}</a> ({self.followers_count:,} 👥){self.note if allow_embedded else ""}</span>'

    @property
    def num_followers(self):
        return self.followers_count if self.followers_count else 0

    @property
    def num_following(self):
        return self.following_count if self.following_count else 0

    def get_url_local(self, server):
        return '/'.join([server,'@'+self.acct])

    @cached_property
    def node_data(self):
        odx={}
        odx['html'] = self._repr_html_(allow_embedded=True)
        odx['shape']='circularImage'
        odx['image'] = self.avatar
        odx['size'] = 25
        odx['text'] = self.display_name
        odx['node_type']='user'
        odx['color']='#111111'
        return odx