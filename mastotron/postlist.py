from .imports import *

class PostList(UserList):
    def __init__(self, data_iter=[]):
        from .post import Post
        data = [Post(x) for x in data_iter]
        data = [x for x in data if x is not None and x.is_valid]
        super().__init__(data)

    def __hash__(self):
        return hash('____'.join(p._id for p in self))
    
    def sort_chron(self):
        self.sort(key=lambda post: post.timestamp if post.timestamp else 0, reverse=False)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    def network(self):
        from .postnet import PostNet
        return PostNet(self)

    @property
    def g(self): return self.network.g
    def graph(self, *args, **kwargs): return self.network.graph(*args,**kwargs)

                


    @property
    def posters(self):
        return {post.author for post in self}
