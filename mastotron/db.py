from .imports import *
# from sqlmodel import Session, SQLModel, create_engine

# class TronDB:
#     def __init__(self, name='testdb'):
#         self.name=name
#         self.engine = create_engine(f'sqlite:///{self.path}')
#         SQLModel.metadata.create_all(self.engine)
    
#     @property
#     def path(self):
#         from mastotron import path_data
#         return os.path.join(path_data, f'{self.name}.sqlite')
    
#     def connect(self): return Session(self.engine)
#     def __enter__(self): return self.connect()
#     def __exit__(self,*x,**y): pass
    


from blitzdb import Document, FileBackend
class PostDB(Document): pass
class PosterDB(Document): pass

dbconn = None
gdb = None

class TronDB:
    @property
    def conn(self):
        global dbconn
        
        if dbconn is None: 
            log.debug(f'CONNECTING TO: {path_blitzdb}')
            dbconn = FileBackend(path_blitzdb)
        
        return dbconn
    
    def save(self, obj):
        self.conn.save(obj)
        self.conn.commit()    

    def get_post(self, uri):
        try:
            return dict(self.conn.get(PostDB,{'_id' : uri}))
        except PostDB.DoesNotExist:
            return {}

    def set_post(self, post_d):
        _id = post_d.get('_id')
        if _id: post_d = {**self.get_post(_id), **post_d}
        post = PostDB(post_d)
        self.save(post)
    
    def since(self, timestamp):
        return self.conn.filter(
            PostDB,
            {'timestamp' : {'$gte' : timestamp}}
        )
    
    def since_unread(self, timestamp):
        return self.conn.filter(
            PostDB,
            {
                'timestamp' : {'$gte' : timestamp},
                'is_read' : {'$ne' : True},
            }
        )

    @property
    def gdb(self):
        global gdb
        if gdb is None:
            from cog.torque import Graph
            gdb = Graph(
                'cogdb', 
                cog_home=os.path.basename(path_cogdb), 
                cog_path_prefix=os.path.dirname(path_cogdb)
            )
        return gdb
    
    def relate(self, obj1, obj2, rel):
        self.gdb.put(obj1._id,rel,obj2._id)

    def get_relatives(self, obj, rel):
        return [
            d.get('id')
            for d in self.gdb.v(obj._id).out(rel).all().get('result')
        ]

    def get_relative(self, obj, rel):
        el = self.get_relatives(obj, rel)
        return el[0] if el else None