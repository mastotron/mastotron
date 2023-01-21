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
SCORE_TYPE = 'All'




def logmsg(x):
    print(x)
    emit('logmsg',{'msg':str(x)})


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
        else:
            logmsg(f'logged in as {acct}')




def get_acct_name(data={}): return session.get('account')
def get_srvr_name(data={}): return get_acct_name().split('@')[-1].strip()



#########
# GRAPH #
#########

class NodeListener(StreamListener):
    def on_update(self, status):
        url = status.get('url')
        print('got update',url)
        # get post
        post = Post(url)
        if post:
            new_urls.add(post)

@socketio.event
def start_updates(data={}):
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
    for new_url in [x for x in new_urls]:
        print('got push')
        add_post(new_url, with_context=False)
        new_urls.remove(new_url)

@socketio.event
def get_updates(data={}):
    acct = get_acct_name()
    lim = data.get('lim', 50)
    if not acct: return
    
    def iterposts():
        yield from Tron().timeline_iter(acct, timeline_type='home', unread_only=True, lim=lim)
        yield from Tron().latest_iter(mins_ago=60 * 24, unread_only=True)
    
    posts_sent = []
    for i,post in enumerate(iterposts()):
        if i >= lim: break
        
        pdata = add_post(
            post, 
            with_context=False, 
            with_context_recurse=0,
            send_data=True
        )
        if pdata: posts_sent.append(post)
    
    for post in posts_sent:
        add_post(post, with_context=True, with_context_recurse=1, send_data=True)


@socketio.event
def add_context(node_id):
    print('add_context', node_id)
    add_post(node_id, with_context = True, with_context_recurse=0)

@socketio.event
def add_full_context(node_id):
    print('add_full_context', node_id)
    add_post(node_id, with_context = True, with_context_recurse=1)


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










    
    
def get_node_data(post, last_post = None):
    same_author = last_post and last_post.author == post.author

    odx={}
    odx['html'] = post.get_html(
        allow_embedded=False, 
        server=get_srvr_name()
    )
    odx['shape'] = 'circularImage' # if not same_author else 'box'
    odx['image'] = post.author.avatar
    odx['label']=post.label if not post.is_boost else ''
    odx['text'] = post.text if not post.is_boost else 'RT'
    odx['node_type']='post'
    odx['scores'] = post.scores
    odx['score'] = post.scores.get(SCORE_TYPE, np.nan)
    odx['timestamp'] = post.timestamp
    # odx['fixed']=dict(x=False,y=False)
    odx['num_replies'] = post.num_replies

    return odx



def add_post(post, with_context = False, with_context_recurse=0, with_context_progress=False,
        send_data=True, with_context_lim=10):
    global seen_posts
    # seen_posts = set()

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

        
        # nodes.append({'id':post.author._id, **post.author.node_data})
        
        # if not post.in_reply_to or post.in_reply_to.author != post.author:
            # edges.append({'id':post._id+'__'+post.author._id, 'from':post.author._id, 'to':post._id})

        
        if post.in_reply_to and post.in_reply_to.is_valid and not post.in_reply_to.is_read: 
            nodes.append({'id':post._id, **get_node_data(post)})
            nodes.append({'id':post.in_reply_to._id, **get_node_data(post.in_reply_to, post)})
            same_author = post.author == post.in_reply_to.author
            # print(post.author, post.in_reply_to.author, same_author)
            edges.append({ 
                'id':f'{post._id}__in_reply_to__{post.in_reply_to._id}',
                'from':post.in_reply_to._id if 0 else post._id,
                'to':post._id if 0 else post.in_reply_to._id, 
                # 'label':'↩️',
                'edge_type':'in_reply_to',
                'is_same_author':same_author
            })
        
        elif post.in_boost_of and post.in_boost_of.is_valid and not post.in_boost_of.is_read: 
            # add_post(post.in_boost_of)
            # nodes.append({'id':post._id, **get_node_data(post)})
            nodes.append({'id':post.in_boost_of._id, **get_node_data(post.in_boost_of)})

            # edges.append({
            #     'id':f'{post._id}__in_boost_of__{post.in_boost_of._id}',
            #     'from':post._id, 
            #     'to':post.in_boost_of._id,
            #     # 'label':'🔁',
            #     'edge_type':'in_boost_of',
            #     'is_same_author':post.author == post.in_boost_of.author
            # })
        
        elif not post.is_reply and not post.is_boost:
            nodes.append({'id':post._id, **get_node_data(post)})
        
        if nodes or edges:
            odata = dict(nodes=nodes, edges=edges)
            if with_context:
                context = post.get_context(
                    recurse=with_context_recurse, 
                    progress=with_context_progress
                )
                
                for i,post2 in enumerate(tqdm(context)):
                    if i>=with_context_lim: break
                    post2_odata = add_post(
                        post2, 
                        with_context=False,
                        send_data=False
                    )
                    if post2_odata and (post2_odata.get('nodes') or post2_odata.get('edges')):
                        odata = {
                            'nodes':(odata['nodes'] + post2_odata.get('nodes',[])),
                            'edges':(odata['edges'] + post2_odata.get('edges',[]))
                        }

            if send_data and odata: emit('get_updates', odata)
            return odata




if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)
    