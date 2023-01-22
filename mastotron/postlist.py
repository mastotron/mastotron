from .imports import *

class PostList(UserList):
    def __init__(self, data_iter=[], lim=None):
        from .post import Post
        def iterr():
            seen=set()
            for post in data_iter:
                post = Post(post).source
                if post and post not in seen:
                    yield post
                    seen.add(post)
        l=list(islice(iterr(), lim))
        super().__init__(l)

    def __hash__(self):
        return hash('____'.join(p._id for p in self))
    def __add__(self, other):
        return PostList(self.data + other.data)
    
    def sort_chron(self):
        self.sort(key=lambda post: post.timestamp if post.timestamp else 0, reverse=False)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    def network(self):
        from .postnet import PostNet
        return PostNet(self)
    @cached_property
    def net(self): return self.network()
    
    def graph(self, *args, **kwargs): return self.net.graph(*args,**kwargs)
    @property
    def g(self): return self.graph()
    
                


    @property
    def posters(self):
        return {post.author for post in self}
