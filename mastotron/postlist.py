from .imports import *

class PostList(UserList):
    def __init__(self, data=[]):
        data = [*set(data)]
        super().__init__(data)
        self.sort_chron()
    
    def sort_chron(self):
        self.sort(key=lambda post: post.timestamp if post.timestamp else 0, reverse=False)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    @cached_property
    def network(self):
        from .postnet import PostNet
        return PostNet(self)

    @property
    def g(self): return self.network.graph()
                


    @property
    def posters(self):
        return {post.author for post in self}
