from .imports import *

class PostNet:
    def __init__(self, posts):
        from .postlist import PostList
        
        self.posts = (
            PostList(posts)
            if type(posts)!=PostList
            else posts
        )
    
    def graph(self):
        g=nx.DiGraph()
        
        def ensure_node(node):
            if not g.has_node(node._id):
                g.add_node(node._id, **node.data)
        
        def ensure_edge(n1,n2, **eopts):
            if not g.has_edge(n1._id, n2._id):
                g.add_edge(n1._id, n2._id, **eopts)

        for post in self.posts:
            ensure_node(post)
            if post.in_reply_to:
                ensure_node(post.in_reply_to)
                ensure_edge(post, post.in_reply_to, rel='replied_to')
            # for post_reply in post.replies:
                # reply = Post(reply)

        
        return g


    @property
    def g(self): return self.graph()
        
    def to_adjmat(self, g=None):
        if not g: g = self.graph()
        return pd.DataFrame(
            nx.adjacency_matrix(g).todense(),
            columns = g.nodes,
            index = g.nodes
        )

    def to_d3graph(self, g=None):
        from d3graph import d3graph
        if not g: g = self.graph()
        adjmat = self.to_adjmat(g=g)
        d3 = d3graph()
        d3.graph(adjmat)
        
        import palettable
        cmap = palettable.colorbrewer.qualitative.Dark2_7.hex_colors
        


        ntypes = [d.get('node_type','node') for n,d in g.nodes(data=True)]
        nlabels = [d.get('label','?') for n,d in g.nodes(data=True)]
        ntooltips = [d.get('tooltip','?') for n,d in g.nodes(data=True)]
        ntypes_setl = list(set(ntypes))
        
        def ntype(node):
            return g.nodes[node]['node_type']

        def sizer(node, factor=7.5):
            ntyp=ntype(node)
            if ntyp=='post':
                return 2*factor
            elif ntyp=='user':
                return 1*factor
            return .5*factor

        ncolors = [cmap[ntypes_setl.index(ntyp)] for ntyp in ntypes]
        nsizes = [sizer(n) for n in g.nodes()]


        d3.set_node_properties(
            label=nlabels,
            tooltip=ntooltips,
            color='cluster',
            size=nsizes
            # edge_color=ncolors,
            # edge_size=2

        )
        d3.set_edge_properties(directed=True)
        return d3


    def to_pyvis(self, g=None):
        from pyvis.network import Network
        if not g: g = self.graph()
        
        # expand
        for n,d in g.nodes(data=True):
            obj = d.get('obj')
            if d.get('node_type')=='user':
                g.nodes[n]['shape']='circularImage'
                g.nodes[n]['image'] = d.get('obj').avatar
                g.nodes[n]['size'] = 25
            elif d.get('node_type')=='post':
                g.nodes[n]['shape']='box'
                g.nodes[n]['label']=' '.join(w for w in obj.text.split() if w and w[0]!='@')[:40]
                
        # filter
        for n,d in g.nodes(data=True):
            for k,v in list(d.items()):
                if type(v) not in {float,int,str,dict,list}:
                    del g.nodes[n][k]
        
        # make net
        nt = Network(
            width='100%',
            height='800px',
            directed=True,
            cdn_resources = 'remote',    
            notebook=True
        )
        nt.from_nx(g)
        return nt.show('nx.html')




























    # def graph_old(self):
    #     # start graph
    #     G=nx.DiGraph()
    #     # funcs
    #     node2int = {}
    #     int2node = {}
    #     def ensure_post_node(post):
    #         post_name = str(post)
    #         post_id = node2int.get(post_name)
    #         if post_id is None: post_id = G.order()+1

    #         if not G.has_node(post_id):    
    #             node2int[post_name]=post_id
    #             G.add_node(
    #                 post_id,
    #                 name=post_name,
    #                 node_type='post',
    #                 label=post.text[:50],
    #                 text=post.text,
    #                 url=post.url_local,
    #                 obj=post
    #             )
    #         return post_id

    #     def ensure_user_node(user):
    #         user_name = str(user)
    #         user_id = node2int.get(user_name)
    #         if user_id is None: user_id = G.order()+1
    #         if not G.has_node(user_id):
    #             node2int[user_name]=user_id

    #             G.add_node(
    #                 user_id,
    #                 name=user_name,
    #                 node_type='user',
    #                 label = user.display_name,
    #                 text = user.display_name,
    #                 obj = user,
    #                 url = user.url_local
    #             )
    #         return user_id
        
    #     def add_user_post(post):
    #         user = post.author
    #         uid=ensure_user_node(user)

    #         if post.is_boost:
    #             uid2=ensure_user_node(post.in_boost_of.author)
    #             pid=ensure_post_node(post.in_boost_of)
    #             if not G.has_edge(uid,uid2): G.add_edge(uid,uid2)
    #             if not G.has_edge(uid2,pid): G.add_edge(uid2,pid)
    #         else:
    #             pid=ensure_post_node(post)
    #             if not G.has_edge(uid,pid): G.add_edge(uid,pid)

    #         add_replies(post)
    #         return pid

    #     def add_replies(post):
    #         if post.is_reply:
    #             post2 = post.in_reply_to
                
    #             post1id = ensure_post_node(post)
    #             post2id = ensure_post_node(post2)
    #             # post2id = add_user_post(post2)

    #             G.add_edge(post1id, post2id)

    #             add_replies(post2)
    #         # if post.is_boost:
    #         #     post2 = post.in_boost_of
    #         #     post1id = ensure_post_node(post)
    #         #     post2id = add_user_post(post2)
    #         #     # post2id = ensure_post_node(post2)
    #         #     G.add_edge(post1id, post2id)

    #     # build
    #     for post in self.posts:
    #         add_user_post(post)

        
    #     return G