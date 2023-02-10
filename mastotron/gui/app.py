## internal imports
import os,sys
path_app = os.path.realpath(__file__)
path_code = os.path.abspath(os.path.join(path_app,'..','..'))
path_codedir = os.path.abspath(os.path.join(path_code,'..'))
sys.path.insert(0,path_codedir)
from mastotron import *
from mastotron import __version__ as vnum


## external imports
import socket,time,webbrowser,signal
import gevent
import webview
import threading
from engineio.payload import Payload
Payload.max_decode_packets = 500
from threading import Lock,Thread,Event
from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_session import Session
from flask_socketio import SocketIO, send, emit
from mastodon import StreamListener
import os,time,sys,random
from engineio.async_drivers import gevent as gevent_async_driver
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


## constants
MAX_UPDATE=15
CRAWL_LIM=10
CRAWL_WAIT_SEC=60
SEEN=set()
CRAWL_STARTED={}
LSTNR_STARTED={}
new_urls = set()
new_msgs = []
ACCT = None


# @lru_cache
def Tron():
    obj = Mastotron()
    obj._logmsg = logmsg_tron
    return obj

def logmsg_tron(*x,**y):
    global new_msgs
    new_msgs.append(' '.join(str(xx) for xx in x))
    # print('>>>',new_msgs[-1])

def logmsg(*x,**y):
    emitt('logmsg',' '.join(str(xx) for xx in x))
    gevent.sleep(0.1)
def logsuccess(x): emitt('logsuccess',str(x))
def logerror(x): emitt('logerror',str(x))

def emitt(key,val,*vals,broadcast=True,**opts):
    # emit(key,val,*vals,broadcast=broadcast,**opts)
    socketio.emit(key,val,*vals,broadcast=broadcast,**opts)


#####
HOSTPORTURL=f'http://{HOST}:{PORT}'

LINE1=f'MASTOTRON v{vnum}'
LINE2=f'{HOSTPORTURL}'
LINE3='(Visit this URL in your browser.'
LINE4='It\'s been copied to your clipboard.)'
# LINE4='(To exit, hold Ctrl+C or close terminal window.)'
LOGO=r'''                      _        _                   
                     | |      | |                  
  _ __ ___   __ _ ___| |_ ___ | |_ _ __ ___  _ __  
 | '_ ` _ \ / _` / __| __/ _ \| __| '__/ _ \| '_ \ 
 | | | | | | (_| \__ \ || (_) | |_| | | (_) | | | |
 |_| |_| |_|\__,_|___/\__\___/ \__|_|  \___/|_| |_|
'''

ELE=r'''
                 /eeeeeeeeeee\ 
   /RRRRRRRRRR\ /eeeeeeeeeeeee\ /RRRRRRRRRR\ 
  /RRRRRRRRRRRR\|eeeeeeeeeeeee|/RRRRRRRRRRRR\ 
 /RRRRRRRRRRRRRR +++++++++++++ RRRRRRRRRRRRRR\ 
|RRRRRRRRRRRRRR ############### RRRRRRRRRRRRRR| 
|RRRRRRRRRRRRR ######### ####### RRRRRRRRRRRRR| 
 \RRRRRRRRRRR ######### ######### RRRRRRRRRR/ 
   |RRRRRRRRR ########## ######## RRRRRRRR| 
  |RRRRRRRRRR ################### RRRRRRRRR| 
               ######     ###### 
               #####       ##### 
               #nnn#       #nnn#
'''


lwid=max(len(lstr) for lstr in ELE.split('\n'))
WELCOME_MSG = f'''
{ELE.center(lwid)}
{LINE1.center(lwid)}

{LINE2.center(lwid)}

{LINE3.center(lwid)}
{LINE4.center(lwid)}
'''


app = Flask(__name__, static_folder=path_static, template_folder=path_templates)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(path_data, 'flask_session')
Session(app)
# socketio = SocketIO(app, manage_session=False, async_handlers=False)
socketio = SocketIO(app, manage_session=False, async_mode="gevent")
# socketio = SocketIO(app, manage_session=False, async_mode="eventlet")


@app.route("/")
@app.route("/hello/")
@app.route("/hello-vue/")
def postnet(): 
    global ACCT
    acct=session.get('acct')
    if not acct or not Tron().user_is_init(acct): 
        return render_template('login.html', acct=acct, config_d=get_config())
    else:
        ACCT = acct
        return render_template('postnet.html', acct=acct, config_d=get_config())

@app.route('/hello//flaskwebgui-keep-server-alive')
@app.route('/hello/flaskwebgui-keep-server-alive')
@app.route('/flaskwebgui-keep-server-alive')
def keepalive():
    return {'status':200}


def get_config(d={}):
    defaultd={
        'LIM_NODES_GRAPH':12,
        'LIM_NODES_STACK':100,
        'DARKMODE':1,
        'VNUM':vnum,
    }
    sessiond={k:v for k,v in session.items() if k and k[0]!='_'}
    outd = {**defaultd, **sessiond, **d}
    return outd

@socketio.event
def req_config(d={}):
    emitt('res_config',get_config(d))

@socketio.event
def set_config(k,v):
    # print(f'setting config: {k} -> {v}')
    # print(f'{k} in config now =',get_config().get(k))
    session[k]=v

@socketio.event
def set_acct_name(data):
    tron = Tron()
    acct = clean_account_name(data.get('acct'))
    if acct:
        session['acct'] = acct
        if not tron.user_is_init(acct):
            try:
                url = tron.user_auth_url(acct)
                logmsg('Please enter activation code')
                emitt('get_auth_url', {'acct':acct,'url':url} )
            except Exception as e:
                un,server=parse_account_name(acct)
                emitt('server_not_giving_code', {'server':server, 'acct':acct})
    else:
        emitt('invalid_user_name', data)
        

@socketio.event
def do_login(data):
    tron = Tron()
    acct = data.get('acct')
    code = data.get('code')
    if acct and code:
        tron.api_user(acct, code=code, direct_input=False)
        if tron.user_is_init(acct):
            logmsg(f'{acct} logged in')
            emitt('login_succeeded', dict(acct=acct))
        else:
            logmsg(f'{acct} NOT logged in')
            emitt('login_failed', dict(acct=acct))


def get_acct_name(data={}): return data.get('acct', ACCT)
def get_srvr_name(data={}): return parse_account_name(get_acct_name(data))[-1]



#########
# GRAPH #
#########

class NodeListener(StreamListener):
    def __init__(self,acct,*x,**y):
        super().__init__(*x,**y)
        self.acct=acct

    def on_update(self, status):
        url = status.get('url')
        post = Post(url, **status)
        if post:
            update_posts([post], acct=self.acct, force_push=True)

@socketio.event
def start_updates(data={}):
    # print('!!! starting updates !!!')
    acct = get_acct_name(data)
    start_listener(acct)
    gevent.sleep(30)
    start_crawler(acct)
    
def start_crawler(acct):
    if not acct: return
    if acct in CRAWL_STARTED: CRAWL_STARTED[acct].stop()
    CRAWL_STARTED[acct] = crawler = Crawler(acct)
    socketio.start_background_task(crawler.run)

def start_listener(acct):
    if not acct: return
    if acct in LSTNR_STARTED: LSTNR_STARTED[acct].close()

    LSTNR_STARTED[acct]=Tron().api_user(acct).stream_user(
        NodeListener(acct),
        run_async=True
    )



class Crawler():
    def __init__(self, acct, on=True):
        self.acct=acct
        self.on = on
    
    def crawl(self, lim=CRAWL_LIM, sec_between=.1):
        global SEEN
        if not self.on: return
        iterr=Tron().timeline_iter(self.acct, seen=SEEN, max_mins=60*24, lim=lim)
        for i,post in enumerate(iterr):
            if not self.on: return
            print(i,post)
            update_posts([post], acct=self.acct, bg=True)
            gevent.sleep(sec_between)
    
    def wait(self, sec=CRAWL_WAIT_SEC):
        if not self.on: return
        gevent.sleep(sec)
    
    def run(self):
        while self.on:
            self.crawl()
            self.wait()

    def stop(self):
        self.on = False
        gevent.sleep(0.001)



@socketio.event
def get_updates(data={}):
    global SEEN
    acct = get_acct_name(data)
    if not acct: return
    SEEN|=set(data.get('ids_now',[]))
    lim = data.get('lim') if data.get('lim') else get_config().get('LIM_NODES_STACK')
    force_push = data.get('force_push',False)
    only_latest = data.get('only_latest',False)
    max_mins = data.get('max_mins',60*24)
    unread_only=data.get('unread_only',True)
    bg=data.get('bg',False)

    lim=lim if lim<MAX_UPDATE else MAX_UPDATE
    iterr=Tron().timeline_iter(
    # tl=Tron().timeline(
        acct, 
        unread_only=unread_only,
        seen=SEEN,
        max_mins=max_mins,
        lim=lim,
        only_latest=only_latest
    )
    # update_posts(tl, ids_done=SEEN, force_push=force_push)
    # SEEN|={p._id for post in tl for p in post.allcopies}
    posts=[]
    for i,post in enumerate(iterr):
        if len(posts) < lim:
            if lim>1:
                logmsg(f'found {i+1} of {lim}: {post} ({post.datetime_str_h})')
            else:
                logmsg(f'found: {post} ({post.datetime_str_h})')
            posts.append(post)

            update_posts([post], ids_done=SEEN, force_push=force_push, bg=bg, acct=acct)
        else:
            break
    
    # update_posts(posts, ids_done=SEEN, force_push=force_push, bg=bg)
    SEEN|={p._id for post in posts for p in post.allcopies}

        # update_posts(
        #     [post],
        #     ids_done=SEEN, 
        #     force_push=force_push
        # )
        # SEEN|={p._id for p in post.allcopies}



def update_posts(tl, omsg='refreshed', emit_key='get_updates',ids_done=None,unread_only=True, force_push=False, bg=False, acct=None, force_push_once=False):
    global SEEN
    if type(tl)!=PostList: tl=PostList(tl)
    SEEN|={p._id for p in tl}
    if len(tl):
        # print('>',tl)
        tnet = tl.network()
        local_server = parse_account_name(acct)[-1] if acct else get_srvr_name()
        nx_g = tnet.graph(local_server=local_server)
        nx_g.remove_nodes_from(
            n 
            for n,d in list(nx_g.nodes(data=True))
            if (unread_only and d.get('is_read'))
            or (ids_done and d.get('id') in ids_done)
        )
        nodes = [d for n,d in nx_g.nodes(data=True)]
        edges = [d for a,b,d in nx_g.edges(data=True)]

        # print('ne',[d['id'] for d in nodes],[d['id'] for d in edges])

        omsg = f'{len(nodes)+len(edges)} new updates @ {get_time_str()}'
        if nodes or edges:
            odata = dict(nodes=nodes, edges=edges, logmsg=omsg, force_push=force_push, bg=bg, force_push_once=force_push_once)
            # for n in nodes: print('++',n['id'])
            emitt(emit_key, odata)
            # time.sleep(0.1)
            gevent.sleep(.1)
            return True
    
    # omsg = f'no new updates @ {get_time_str()}'
    # logmsg(omsg)
    return False

@socketio.event
def add_context(node_id):
    # print('add_context',node_id)
    post = Post(node_id)
    if post:# unread_convo = PostList(p for p in post.convo if not p.is_read)
        convo = post.convo
        update_posts(convo[:LIM_TIMELINE], force_push_once=True)









@socketio.event
def set_darkmode(darkmode):
    key='DARKMODE'
    session[key] = int(darkmode)

@socketio.event
def set_in_session(dict):
    for k,v in dict.items():
        session[k]=v

@socketio.event
def mark_as_read(node_ids):
    # print('mark_as_read', node_ids)
    for node_id in node_ids:
        post = Post(node_id)
        post.mark_read()









class OpenBrowser(Thread):
    def __init__(self):
        super(OpenBrowser, self).__init__()
    def notResponding(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock.connect_ex((HOST, PORT))
    def run(self):
        while self.notResponding():
            # print('Did not respond')
            gevent.sleep(0.1)
        # print('Responded')
        webbrowser.open_new(f'http://{HOST}:{PORT}/') 


def send_update(nodes=[], edges=[]):
    odata=dict(nodes=nodes, edges=edges)
    emitt('get_updates', odata)
    return odata


def view(**kwargs):
    OpenBrowser().start()

def mainview(**kwargs):
    # view(**kwargs)
    # main(**kwargs)
    browse(app = app, func = main)


def main(debug=False, **kwargs): 
    try:
        import pyperclip
        pyperclip.copy(HOSTPORTURL)
    except Exception:
        pass
    print(WELCOME_MSG)
    try:
        # socketio.start_background_task(crawl_updates)
        # socketio.start_background_task(browse, app=app)
        return socketio.run(
            app, 
            debug=debug, 
            # allow_unsafe_werkzeug=True,
            port=PORT,
            host=HOST
        )
    # except (KeyboardInterrupt,EOFError):
    except AssertionError:
        print('goodbye')
        exit()



def browse(app=None,**kwargs):
    try:
        from screeninfo import get_monitors
        m = get_monitors()[0]
        width = m.width
        height = m.height
    except Exception:
        width = 1400
        height = 1100

    with app.app_context():
        gevent.sleep(1)
        webview.create_window(
            title=f'Mastotron {vnum}', 
            url=f'http://{HOST}:{PORT}',
            fullscreen=False,
            width=width,
            height=height,
            min_size=(400,300),
            frameless=False,
            easy_drag=True,
            text_select=True,
            confirm_close=True,
        )
        return webview.start(
            private_mode=False,
            storage_path=path_srvr,
            debug=True,
            **kwargs
        )



if __name__=='__main__': mainview(debug=False)