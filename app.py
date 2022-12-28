import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_socketio import SocketIO, send, emit

from mastotron import Mastotron

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
socket = SocketIO(app)
Session(app)

tron = None


@app.route("/")
def postnet(): return render_template('postnet.html')
    
@socket.event
def set_acct_name(data):
    global tron

    acct = data.get('account')
    if acct:
        session['account'] = acct
        tron = Mastotron(acct)
        if not tron.user_is_init():
            logmsg('Please enter activation code')
            emit('get_auth_url', {'url':tron.auth_request_url()} )
        else:
            logmsg(f'logged in as {acct}')

@socket.event
def do_login(data):
    print(data)
    global tron
    acct = data.get('account')
    code = data.get('code')
    tron = Mastotron(acct, code=code)
    emit('logged_in', {'msg':'Successfully logged in'})

@socket.event
def get_updates(data):
    if not tron: return
    
    g = tron.timeline(max_posts=20, hours_ago=1).network().graph()

    def get_node(d):
        odx=dict()
        obj=d.get('obj')
        odx['label']=d.get('label')
        odx['html'] = obj._repr_html_(allow_embedded=False)
        if d.get('node_type')=='user':
            odx['shape']='circularImage'
            odx['image'] = obj.avatar
            odx['size'] = 25
            odx['text'] = obj.display_name
            odx['node_type']='user'
        elif d.get('node_type')=='post':
            odx['shape']='box'
            odx['label']=obj.label
            odx['text'] = obj.text
            odx['node_type']='post'
        return odx

    nodes = [
        dict(
            id=node,
            **get_node(d)
        )
        for node,d in g.nodes(data=True)
    ]
    for d in nodes:
        print('>>',d)

    edges = [
        {
            'id':ei+1,
            'from':n1, 
            'to':n2,
            
        }
        for ei,(n1,n2,d) in enumerate(g.edges(data=True))
    ]
    for d in edges:
        print('>>>',d)
    
    emit('get_updates', dict(nodes=nodes, edges=edges))


def logmsg(x):
    print(x)
    emit('logmsg',{'msg':str(x)})