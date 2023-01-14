from .imports import *

def get_api():
    global API
    return API

def set_api(mastotron_obj):
    global API
    API = mastotron_obj



def parse_account_name(acct):
    un, server = '', ''
    acct = acct.strip()
    
    if acct and '@' in acct:
        if acct.startswith('@'):
            return parse_account_name(acct[1:])

        elif acct.count('@')>1:
            return parse_account_name(acct.split('/@',1)[-1])

        elif acct.startswith('http'):
            server, un = acct.split('/@')
            un = un.split('/')[0]
            server = server.split('://',1)[-1].split('/')[0]

        elif acct.count('@')==1:
            un, server = acct.split('@',1)
            server = server.split('/')[0]

    return un,server

def get_server_name(server):
    return server.split('://',1)[-1].split('/',1)[0]

def get_status_id(url):
    for x in reversed(url.split('/')):
        if x and x.isdigit():
            return int(x)

def get_account_name(x): return parse_account_name(x)[0]

def get_server_account_status_id(x):
    return (
        get_server_name(x),
        get_account_name(x),
        get_status_id(x)
    )

TRON=None
def get_tron():
    global TRON
    if TRON is None: 
        from .mastotron import Mastotron
        TRON=Mastotron()
    return TRON

class DictModel:
    def __init__(self, data_d={}, **kwargs):
        self._data = {**(data_d if data_d else {}), **(kwargs if kwargs else {})}

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return self._data.get(name)

def to_uri(url): 
    if url.count('@')>=2:
        return url
    else:
        url = url.replace('/users/','/@').replace('/statuses/','/')
        un,server = parse_account_name(url)
        status_ids = [y for y in url.split('/') if y.isdigit()]
        if status_ids:
            status_id = status_ids[0]
            return f'https://{server}/@{un}/{status_id}'
        return ''