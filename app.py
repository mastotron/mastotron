import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from mastotron import Mastotron

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

tron = None
ACCT = None
CODE = None


@app.route('/get_acct_name')
def get_acct_name(account='', force=True):
    global ACCT

    account = request.args.get('account',account)
    force = request.args.get('force',force)
    if not account:
        if not force: account = session.get('account')
        if not account:
            return render_template('login.html')
    else:
        session['account'] = account
    ACCT = account
    return ACCT

@app.route('/get_auth_code',methods=["GET","POST"])
def get_auth_code(code='',account='',force=True):
    global CODE

    code = request.form.get('code',code)
    if not code:
        if not force: code = session.get('code')
        if not code:
            acct = get_acct_name(account=account, force=force)
            tron = Mastotron(acct)
            url = tron.auth_request_url()
            return render_template('code.html', code=code, url=url)
    else:
        session['code'] = code
    CODE = code
    return code
    
@app.route('/get_auth_url')
def get_auth_url(account='',force=True):
    
    acct = get_auth_name()


    if not code:
        if not force: code = session.get('code')
        if not code:
            acct = get_acct_name(account=account, force=force)
            tron = Mastotron(acct)
            url = tron.auth_request_url()
            return render_template('code.html', code=code, url=url)
    else:
        session['code'] = code
    CODE = code
    return code
    



@app.route('/login')
def login():
    global tron
    if tron is None:
        if not ACCT: return get_acct_name()
        print(['!?!?',acct])
        tron = Mastotron(acct)
        if not tron.user_is_init():
            code = get_auth_code(account=acct)
            return code
            tron.init_user(code=code)
    return redirect(url_for('postnet'))

@app.route("/")
def postnet():
    if tron is None:
        return redirect(url_for('login'))
    
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

    edges = [
        {'from':n1, 'to':n2}
        for n1,n2,d in g.edges(data=True)
    ]

    return render_template(
        'postnet.html', 
        nodes = nodes, 
        edges = edges
    )