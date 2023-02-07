from .imports import *

class PostList(UserList):
    def __init__(self, data_iter=[], lim=None):
        from .post import Post
        # def iterr():
        #     seen=set()
        #     for post in data_iter:
        #         post = Post(post)
        #         if post:
        #             post = post.source
        #             if post not in seen:
        #                 yield post
        #                 seen.add(post)
        def iterr(): 
            yield from (Post(x) for x in data_iter)
        l=list(islice(iterr(), lim))
        super().__init__(l)
        self.sort_chron()

    def __str__(self):
        return str([p._id for p in self])

    def __hash__(self):
        return hash('____'.join(p._id for p in self))
    def __add__(self, other):
        def iterr():
            yield from self
            yield from other
        return PostList(iterr())
    
    def __sub__(self, other):
        bad_ids = set(other)
        def iterr():
            for x in self:
                if x not in bad_ids:
                    yield x
        return PostList(iterr())


    
    def sort_chron(self):
        self.sort(key=lambda post: post.timestamp if post.timestamp else 0, reverse=False)

    def sort_score(self, score_type=SCORE_TYPE):
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

    def interrelate(self):
        context_d = dict((post._data.get('id'), post) for post in self)
        for post in self:
            if post.is_reply and not post.out(REL_IS_REPLY_TO):
                post2 = context_d.get(post.in_reply_to_id)
                if post2:
                    post.relate(post2, rel=REL_IS_REPLY_TO)
                    print(post,'-->',post2)