from .imports import *

class Poster(AttribAccessDict):

    def __init__(self,*args,_tron=None,**kwargs):
        ## init self
        self._tron = (get_api() if not _tron else _tron)
        ## pass into dict init
        super().__init__(*args, **kwargs)

    
    def __hash__(self):
        return hash(self.acct)
    
    def __eq__(self, other):
        return self.acct == other.acct

    def __repr__(self):
        return f'Poster({self.acct})'

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


