from .imports import *

class PostList(UserList):
    def __init__(self, l):
        super().__init__(l)
    
    def sort_chron(self):
        self.sort(key=lambda post: post.created_at, reverse=True)

    def sort_score(self, score_type='All'):
        self.sort(key=lambda post: post.score(score_type), reverse=True)
    
    def network(self):
        return PostNet(self)

    @property
    def posters(self):
        return {post.author for post in self}
