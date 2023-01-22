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


def logmsg(x):
    log.debug(x)
    emit('logmsg',str(x))


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
    if not session.get('account'): session['account']='heuser@zirk.us'
    return render_template('postnet.html', account=session.get('account',''))

@app.route('/hello//flaskwebgui-keep-server-alive')
@app.route('/hello/flaskwebgui-keep-server-alive')
@app.route('/flaskwebgui-keep-server-alive')
def keepalive():
    return {'status':200}
    
@socketio.event
def set_acct_name(data):
    tron = Tron()
    acct = data.get('account')
    if acct:
        session['account'] = acct
        if not tron.user_is_init(acct):
            logmsg('Please enter activation code')
            emit('get_auth_url', {'url':tron.auth_request_url()} )
        # else:
            # logmsg(f'logged in as {acct}')




def get_acct_name(data={}): return session.get('account')
def get_srvr_name(data={}): return get_acct_name().split('@')[-1].strip()



#########
# GRAPH #
#########

class NodeListener(StreamListener):
    def on_update(self, status):
        url = status.get('url')
        post = Post(url)
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
        omsg='push updated',
        ids_done=set(data.get('ids_now',[]))
    )
        


@socketio.event
def get_updates(data={}):
    acct = get_acct_name()
    if not acct: return
    tl = Tron().timeline(acct, lim=10)
    update_posts(
        tl,
        omsg='timeline updated',
        ids_done=set(data.get('ids_now',[]))
    )
        

def get_datetime_str():
    import datetime as dt
    return str(dt.datetime.now()).split('.',1)[0]
def get_time_str():
    import datetime as dt
    return str(dt.datetime.now()).split('.',1)[0].split()[-1]

def update_posts(tl, omsg='refreshed', emit_key='get_updates',ids_done=None):
    if len(tl):
        tnet = tl.network()
        nx_g = tnet.graph()
        nx_g.remove_nodes_from(
            n 
            for n,d in list(nx_g.nodes(data=True))
            if d.get('is_read')
            or (ids_done and d.get('id') in ids_done)
        )       
        nodes = [d for n,d in nx_g.nodes(data=True)]
        edges = [d for a,b,d in nx_g.edges(data=True)]
        
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
    if post:
        context = post.get_context(lim=5, as_list=False, recurse=0, interrelate=False)
        if len(context):
            update_posts(context)









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









def get_edge_data(obj1, obj2, rel, **kwargs):
    return { 
        'id':f'{obj1._id}__{rel}__{obj2._id}',
        'from':obj1._id,
        'to':obj2._id, 
        'edge_type':rel,
        **kwargs
    }


def send_update(nodes=[], edges=[]):
    odata=dict(nodes=nodes, edges=edges)
    emit('get_updates', odata)
    return odata







if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)
    