from .imports import *
gdb = None
class TronDB:
    @property
    def gdb(self):
        global gdb
        if gdb is None:
            from cog.torque import Graph
            # try:
            gdb = Graph(
                'cogdb', 
                cog_home=os.path.basename(path_cogdb), 
                cog_path_prefix=os.path.dirname(path_cogdb),
                enable_caching=False
            )
            # except Exception as e:
                # # print(f'!! {e} !!')
                # rmfile(path_cogdb)
                # gdb = Graph(
                #     'cogdb', 
                #     cog_home=os.path.basename(path_cogdb), 
                #     cog_path_prefix=os.path.dirname(path_cogdb)
                # )

        return gdb
    
    def relate(self, obj1, obj2, rel):
        id1=str(obj1)
        id2=str(obj2)
        rel=str(rel)
        if id1 and id2 and rel:
            self.gdb.put(id1,rel,id2)
    
    def unrelate(self, obj1, obj2, rel):
        id1=str(obj1)
        id2=str(obj2)
        rel=str(rel)
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