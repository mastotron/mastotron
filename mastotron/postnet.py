from .imports import *

class PostNet:
    def __init__(self, posts):
        from .postlist import PostList
        self.posts = (
            PostList(posts)
            if type(posts)!=PostList
            else posts
        )
    
    def graph(self, local_server=''):
        g=nx.DiGraph()
        
        def ensure_node(node):
            ndata = node.get_node_data(local_server=local_server)
            nid = ndata.get('id')
            if not g.has_node(nid):
                g.add_node(nid, **ndata)
            return nid
        
        def ensure_edge(n1,n2,rel='',**eopts):
            n1id=ensure_node(n1)
            n2id=ensure_node(n2)
            if not g.has_edge(n1id, n2id):
                eopts['id']=f'{n1id}__{rel}__{n2id}'
                eopts['rel']=rel
                eopts['from']=n1id
                eopts['to']=n2id
                g.add_edge(n1id, n2id, **eopts)
            return (n1id,n2id)

        def add_post(post):
            if post.is_boost_of:
                return add_post(post.is_boost_of)
            
            ensure_node(post)
            if post.is_reply_to: 
                ensure_edge(post, post.is_reply_to, rel='replied_to')
            
        
        for post in self.posts: add_post(post)
        
        return g

    @cached_property
    def g(self): return self.graph()
        
    def to_adjmat(self, g=None):
        if not g: g = self.graph()
        return pd.DataFrame(
            nx.adjacency_matrix(g).todense(),
            columns = g.nodes,
            index = g.nodes
        )



        