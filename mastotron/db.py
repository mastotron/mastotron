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
        id1=str(obj1)
        id2=str(obj2)
        if id1 and id2 and rel:
            self.gdb.put(id1,rel,id2)
    
    def unrelate(self, obj1, obj2, rel):
        id1=str(obj1)
        id2=str(obj2)
        if id1 and id2 and rel:
            self.gdb.drop(id1,rel,id2)

    def get_rels_out(self, obj, rel):
        return [d.get('id') for d in self.gdb.v(str(obj)).out(rel).all().get('result') if d.get('id')]
    def get_rels_inc(self, obj, rel):
        return [d.get('id') for d in self.gdb.v(str(obj)).inc(rel).all().get('result') if d.get('id')]
    def get_rels(self, obj, rel):
        return self.get_rels_out(obj,rel) + self.get_rels_inc(obj,rel)

    def get_rel_out(self, obj, rel):
        rels=self.get_rels_out(obj,rel)
        return rels[0] if rels else None
    def get_rel_inc(self, obj, rel):
        rels=self.get_rels_inc(obj, rel)
        return rels[0] if rels else None
    def get_rel(self, obj, rel):
        rels = self.get_rels(obj,rel)
        return rels[0] if rels else None

    