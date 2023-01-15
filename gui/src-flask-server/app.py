# make sure to use eventlet and call eventlet.monkey_patch()
import eventlet
eventlet.monkey_patch()

import os,sys,random,time
from threading import Lock
sys.path.insert(0,'/Users/ryan/github/mastotron')
from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_session import Session
from flask_socketio import SocketIO, send, emit
from mastotron import Tron, path_data, PostModel, Post, encodeURIComponent
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
        print('got update',url)
        # get post
        post = Post(url)
        if post:
            new_urls.add(post)

STARTED=None
@socketio.event
def start_updates(data={}):
    global STARTED
    if not STARTED:
        print('start_updates')
        acct = get_acct_name(data)
        Tron().api_user(acct).stream_user(NodeListener(), run_async=True)
        STARTED=True

@socketio.event
def get_pushes(data={}):
    for new_url in [x for x in new_urls]:
        add_post(new_url, with_context=False)
        new_urls.remove(new_url)

@socketio.event
def get_updates(data={}):
    print('get_updates')
    acct = get_acct_name()
    if acct:
        for post in Tron().timeline_iter(acct, timeline_type='home'):
            add_post(post, with_context=True)
        for post in Tron().latest_iter():
            add_post(post, with_context=True)

@socketio.event
def add_context(node_id):
    print('add_context', node_id)
    add_post(node_id, with_context = True)
    
@socketio.event
def mark_as_read(node_ids):
    print('mark_as_read', node_ids)
    for node_id in node_ids:
        post = Post(node_id)
        post.mark_read()
    
    
    




svg_str='''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400"><rect x="0" y="0" width="100%" height="100%" fill="#7890A7" stroke-width="5" stroke="#ffffff" ></rect><foreignObject x="1" y="1" width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:40px">[[HTML]]</div></foreignObject></svg>'''

def get_svg_url(svg_str):
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg_str)
    
odx={}
# odx['html'] = self._repr_html_(allow_embedded=True)
# odx['shape']='circularImage'
# odx['image'] = self.avatar
# odx['size'] = 25
# odx['text'] = self.display_name
# odx['node_type']='user'
# odx['color']='#111111'
def get_node_data(post):
    odx={}
    odx['html'] = post.get_html(allow_embedded=False)
    # odx['shape']='box'
    # odx['shape'] = 'image'
    odx['shape'] = 'circularImage'
    # odx['image'] = get_svg_url(svg_str.replace('[[HTML]]', odx['html']))
    odx['image'] = post.author.avatar
    odx['label']=post.label[:20] if not post.is_boost else ''
    odx['text'] = post.text if not post.is_boost else 'RT'
    odx['node_type']='post'
    # odx['color'] = '#1f465c' if post.is_reply else '#061f2e'
    return odx



seen_posts = set()
def add_post(post, with_context = False):
    global seen_posts

    if not post: return
    try:
        post = Post(post) if type(post)==str else post
    except Exception as e:
        print(f'!! {e} !!')
        return
    
    nodes = []
    edges = []

    if post.is_valid and post.author.is_valid and not post.is_read:
        if post in seen_posts: return
        seen_posts.add(post)

        nodes.append({'id':post._id, **get_node_data(post)})
        # nodes.append({'id':post.author._id, **post.author.node_data})
        
        # if not post.in_reply_to or post.in_reply_to.author != post.author:
            # edges.append({'id':post._id+'__'+post.author._id, 'from':post.author._id, 'to':post._id})

        if post.in_reply_to and post.in_reply_to.is_valid: 
            add_post(post.in_reply_to)
            edges.append(
                {'id':post.in_reply_to._id+'__'+post._id, 
                'from':post._id, 
                'to':post.in_reply_to._id,
                'label':'📩'
            })
        
        if post.in_boost_of and post.in_boost_of.is_valid: 
            add_post(post.in_boost_of)
            edges.append(
                {'id':post._id+'__'+post.in_boost_of._id, 
                'from':post._id, 
                'to':post.in_boost_of._id,
                'label':'🔁'}
            )
        
        emitt('get_updates', dict(nodes=nodes, edges=edges))


    if with_context:
        for post in post.context:
            add_post(post, with_context=False)




if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)
    