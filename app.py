import os
from flask import Flask, render_template
from mastotron import Mastotron

app = Flask(__name__)
tron = Mastotron('heuser@zirk.us')




@app.route("/")
def postnet():
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