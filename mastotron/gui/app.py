# make sure to use eventlet and call eventlet.monkey_patch()
import eventlet
eventlet.monkey_patch()
import os,sys; sys.path.insert(0,'/Users/ryan/github/mastotron')

from mastotron import *
from threading import Lock
from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_session import Session
from flask_socketio import SocketIO, send, emit
from mastodon import StreamListener
import os,time,sys,random

namespace = 'mastotron.web'
seen_posts = set()
STARTED=None
new_urls = set()


def logmsg(x): emit('logmsg',str(x))
def logsuccess(x): emit('logsuccess',str(x))
def logerror(x): emit('logerror',str(x))

#####
app = Flask(__name__)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(path_data, 'flask_session')
Session(app)
socketio = SocketIO(app, manage_session=False, async_mode="threading")


@app.route("/")
@app.route("/hello/")
@app.route("/hello-vue/")
def postnet(): 
    acct=session.get('acct')
    if not acct or not Tron().user_is_init(acct): 
        return render_template('login.html')
    
    return render_template('postnet.html', acct=acct, minnodes=LIM_TIMELINE)

@app.route('/hello//flaskwebgui-keep-server-alive')
@app.route('/hello/flaskwebgui-keep-server-alive')
@app.route('/flaskwebgui-keep-server-alive')
def keepalive():
    return {'status':200}
    
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
                emit('get_auth_url', {'acct':acct,'url':url} )
            except Exception as e:
                un,server=parse_account_name(acct)
                emit('server_not_giving_code', {'server':server, 'acct':acct})
    else:
        emit('invalid_user_name', data)
        

@socketio.event
def do_login(data):
    tron = Tron()
    acct = data.get('acct')
    code = data.get('code')
    if acct and code:
        tron.api_user(acct, code=code, direct_input=False)
        if tron.user_is_init(acct):
            logmsg(f'{acct} logged in')
            emit('login_succeeded', dict(acct=acct))
        else:
            logmsg(f'{acct} NOT logged in')
            emit('login_failed', dict(acct=acct))


def get_acct_name(data={}): return session.get('acct')
def get_srvr_name(data={}): return parse_account_name(get_acct_name())[-1]



#########
# GRAPH #
#########

class NodeListener(StreamListener):
    def on_update(self, status):
        url = status.get('url')
        post = Post(url, **status)
        if post:
            new_urls.add(post)

@socketio.event
def start_updates(data={}):
    # return
    global seen_posts, STARTED
    seen_posts = set()
    if not STARTED:
        print('start_updates')
        acct = get_acct_name(data)
        Tron().api_user(acct).stream_user(
            NodeListener(), 
            run_async=True
        )
        STARTED=True

@socketio.event
def get_pushes(data={}):
    global new_urls
    new_posts = PostList(new_urls)
    new_urls = set()
    update_posts(
        new_posts, 
        omsg='push updated'
    )


@socketio.event
def get_updates_orig(data={}):
    acct = get_acct_name()
    if not acct: return
    unread_only = data.get('unread_only',True)
    lim = data.get('lim',LIM_TIMELINE)
    tl = Tron().timeline_unread(acct, lim=LIM_TIMELINE, incl_now=False, unread_only=unread_only)
    update_posts(tl)



@socketio.event
def get_updates(data={}):
    acct = get_acct_name()
    if not acct: return
    unread_only = data.get('unread_only',True)
    lim = data.get('lim',LIM_TIMELINE)
    i=0
    batchsize=1
    l=[]
    for post in Tron().timeline_iter(acct):
        if not unread_only or not post.is_read:
            i+=1
            l.extend(post.convo)
            if len(l)>=batchsize:
                update_posts(PostList(l))
                l=[]
                # time.sleep(.5)
            if i>=lim: 
                if l: update_posts(PostList(l))
                break



    # update_posts(tl,omsg='timeline updated',ids_done=set(data.get('ids_now',[])))
        


def update_posts(tl, omsg='refreshed', emit_key='get_updates',ids_done=None,unread_only=True):
    if len(tl):
        tnet = tl.network()
        nx_g = tnet.graph(local_server=get_srvr_name())
        nx_g.remove_nodes_from(
            n 
            for n,d in list(nx_g.nodes(data=True))
            if (unread_only and d.get('is_read'))
            or (ids_done and d.get('id') in ids_done)
        )
        nodes = [d for n,d in nx_g.nodes(data=True)]
        edges = [d for a,b,d in nx_g.edges(data=True)]
        # print('nodes',len(nodes),'edges',len(edges))

        omsg = f'{len(nodes)} new updates @ {get_time_str()}'
        if nodes or edges:
            odata = dict(nodes=nodes, edges=edges, logmsg=omsg)
            emit(emit_key, odata)
            return True
    
    omsg = f'no new updates @ {get_time_str()}'
    logmsg(omsg)
    return False

@socketio.event
def add_context(node_id):
    print('add_context',node_id)
    post = Post(node_id)
    if post:# unread_convo = PostList(p for p in post.convo if not p.is_read)
        convo = post.convo
        update_posts(convo[:LIM_TIMELINE])









@socketio.event
def set_darkmode(darkmode):
    key='DARKMODE'
    session[key] = int(darkmode)

@socketio.event
def mark_as_read(node_ids):
    print('mark_as_read', node_ids)
    for node_id in node_ids:
        post = Post(node_id)
        post.mark_read()








def send_update(nodes=[], edges=[]):
    odata=dict(nodes=nodes, edges=edges)
    emit('get_updates', odata)
    return odata







if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)
    