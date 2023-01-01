from .imports import *

class Poster(AttribAccessDict):

    def __init__(self,*args,_tron=None,**kwargs):
        ## init self
        self._tron = (get_api() if not _tron else _tron)
        ## pass into dict init
        super().__init__(*args, **kwargs)

    @property
    def account(self):
        un, server = parse_account_name(self.url)
        return f'{un}@{server}'
    @property
    def uri(self): return self.url

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
        return self.acct == other.acct

    def __repr__(self):
        return f'Poster({self.acct})'

    @cached_property
    def html(self): return self._repr_html_(allow_embedded=True)

    @cached_property
    def text(self): return unhtml(self.note).strip() if self.note else ''

    def _repr_html_(self, allow_embedded=False, **kwargs):
        return f'<div class="author"><img src="{self.avatar}" /> <a href="{self.url_local}" target="_blank">{self.display_name}</a> ({self.followers_count:,} 👥){self.note if allow_embedded else ""}</div>'

    @property
    def num_followers(self):
        return self.followers_count

    @property
    def num_following(self):
        return self.following_count

    @property
    def url_local(self):
        return self.get_url_local()
    
    def get_url_local(self):
        return '/'.join([
            self._tron.server,
            '@'+self.acct,
        ])


