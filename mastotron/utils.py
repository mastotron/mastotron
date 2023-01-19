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
    if not url: return ''
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

def encodeURIComponent(x):
    from urllib.parse import quote
    return quote(x, safe="!~*'()")


def test_encodeURIComponent():
    inp='''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="65"><rect x="0" y="0" width="100%" height="100%" fill="#7890A7" stroke-width="20" stroke="#ffffff" ></rect><foreignObject x="15" y="10" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:40px"> <em>I</em> am<span style="color:white; text-shadow:0 0 20px #000000;"> HTML in SVG!</span></div></foreignObject></svg>'''
    out='''%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22390%22%20height%3D%2265%22%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%22100%25%22%20height%3D%22100%25%22%20fill%3D%22%237890A7%22%20stroke-width%3D%2220%22%20stroke%3D%22%23ffffff%22%20%3E%3C%2Frect%3E%3CforeignObject%20x%3D%2215%22%20y%3D%2210%22%20width%3D%22100%25%22%20height%3D%22100%25%22%3E%3Cdiv%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxhtml%22%20style%3D%22font-size%3A40px%22%3E%20%3Cem%3EI%3C%2Fem%3E%20am%3Cspan%20style%3D%22color%3Awhite%3B%20text-shadow%3A0%200%2020px%20%23000000%3B%22%3E%20HTML%20in%20SVG!%3C%2Fspan%3E%3C%2Fdiv%3E%3C%2FforeignObject%3E%3C%2Fsvg%3E'''
    assert encodeURIComponent(inp) == out





svg_str='''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect x="0" y="0" width="100%" height="100%" fill="#7890A7" stroke-width="5" stroke="#ffffff" ></rect><foreignObject x="1" y="1" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:40px">[[HTML]]</div></foreignObject></svg>'''


def get_svg_url(svg_str):
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg_str)
