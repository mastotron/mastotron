# make sure to use eventlet and call eventlet.monkey_patch()
import eventlet
eventlet.monkey_patch()

import os,sys,random,time
from threading import Lock
sys.path.insert(0,'/Users/ryan/github/mastotron')
from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_session import Session
from flask_socketio import SocketIO, send, emit
from mastotron import Tron, path_data, PostModel
from mastodon import StreamListener

namespace = 'mastotron.web'

def emitt(name, data, **kwargs):
    # kwargs['namespace']=namespace
    emit(name, data, **kwargs)


def logmsg(x):
    print(x)
    emitt('logmsg',{'msg':str(x)})

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
            emitt('get_auth_url', {'url':tron.auth_request_url()} )
        else:
            logmsg(f'logged in as {acct}')



# @socketio.event
# def do_login(data):
#     global tron
#     acct = data.get('account')
#     code = data.get('code')
#     tron = Tron()#Mastotron(acct, code=code)
#     emitt('logged_in', {'msg':'Successfully logged in'})



def get_acct_name(data={}):
    return session.get('account')


#########
# GRAPH #
#########

new_urls = set()
class NodeListener(StreamListener):
    def on_update(self, status):
        url = status.get('url')
        post = Tron().post(url)
        if post: 
            new_urls.add(post)


@socketio.event
def start_updates(data={}):
    for post in Tron().latest():
        add_post(post)
    return
    acct = get_acct_name(data)
    Tron().api_user(acct).stream_local(NodeListener(), run_async=True)


@socketio.event
def get_updates(data={}):
    print('get_updates')

    acct = get_acct_name()
    if acct:
        for post in Tron().timeline_iter(acct, timeline_type='local'):
            add_post(post)


seen_posts = set()
def add_post(post):
    global seen_posts

    if not post: return
    post = Tron().post(post) if type(post)==str else post
    

    nodes = []
    edges = []

    if post.is_valid() and post.author.is_valid():
        if post in seen_posts: return
        seen_posts.add(post)
        print(f'>> adding post: {post}')

        nodes.append({'id':post.uri, **post.node_data})
        nodes.append({'id':post.author.uri, **post.author.node_data})

        if not post.in_reply_to: 
            edges.append({'id':post.uri+'__'+post.author.uri, 'from':post.author.uri, 'to':post.uri})
        else:
            add_post(post.in_reply_to)
            edges.append({'id':post.in_reply_to.uri+'__'+post.uri, 'from':post.in_reply_to.uri, 'to':post.uri})

        if post.in_boost_of: 
            add_post(post.in_boost_of)
            edges.append({'id':post.uri+'__'+post.in_boost_of.uri, 'from':post.uri, 'to':post.in_boost_of.uri})
        
        
        emitt('get_updates', dict(nodes=nodes, edges=edges))







if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)
    