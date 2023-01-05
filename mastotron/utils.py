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

