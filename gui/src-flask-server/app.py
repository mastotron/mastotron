import os,sys,random
sys.path.insert(0,'/Users/ryan/github/mastotron')
print('PATH',sys.path)
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_socketio import SocketIO, send, emit
from mastotron import Mastotron, path_data


app = Flask(__name__)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(path_data, 'flask_session')
Session(app)
socketio = SocketIO(app, manage_session=False, async_mode="threading")



tron = None


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
    global tron
    print('??',data)
    acct = data.get('account')
    print('?? ??',acct)

    if acct:
        session['account'] = acct
        print('session!',session)
        tron = Mastotron(acct)
        if not tron.user_is_init():
            logmsg('Please enter activation code')
            emit('get_auth_url', {'url':tron.auth_request_url()} )
        else:
            logmsg(f'logged in as {acct}')

@socketio.event
def do_login(data):
    global tron
    acct = data.get('account')
    code = data.get('code')
    tron = Mastotron(acct, code=code)
    emit('logged_in', {'msg':'Successfully logged in'})



@socketio.event
def get_updates(data):
    if not tron: return
    
    g = tron.timeline(max_posts=20, hours_ago=1).network().graph()
    print(g.order(), g.size())

    def get_node(d):
        odx=dict()
        obj=d.get('obj')
        odx['label']=d.get('label')
        odx['url'] = d.get('url')
        if d.get('node_type')=='user':
            odx['html'] = obj._repr_html_(allow_embedded=True)
            odx['shape']='circularImage'
            odx['image'] = obj.avatar
            odx['size'] = 25
            odx['text'] = obj.display_name
            odx['node_type']='user'
            odx['color']='#111111'
        elif d.get('node_type')=='post':
            odx['html'] = obj._repr_html_(allow_embedded=False)
            odx['shape']='box'
            odx['label']=obj.label
            odx['text'] = obj.text
            odx['node_type']='post'
            odx['color'] = '#1f465c' if not obj.is_reply else '#061f2e'
        return odx

    nodes = [
        dict(
            id=node,
            **get_node(d)
        )
        for node,d in g.nodes(data=True)
    ]

    edges = [
        {
            'id':ei+1,
            'from':n1, 
            'to':n2,
            
        }
        for ei,(n1,n2,d) in enumerate(g.edges(data=True))
    ]
    
    emit('get_updates', dict(nodes=nodes, edges=edges))
    logmsg('refreshed')




def logmsg(x):
    print(x)
    emit('logmsg',{'msg':str(x)})


if __name__=='__main__': 
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)