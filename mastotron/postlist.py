from .imports import *

class PostList(UserList):
    def __init__(self, l):
        l = [x for x in l if x is not None]
        super().__init__(l)
        self.sort_chron()
    
    def sort_chron(self):
        self.sort(key=lambda post: post.timestamp if post.timestamp else 0, reverse=True)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    def network(self):
        from .postnet import PostNet
        return PostNet(self)

    @property
    def posters(self):
        return {post.author for post in self}
