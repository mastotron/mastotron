from .imports import *

class GraphDB:
    def __init__(self, account_name_or_mastotron_obj, name='graphdb'):
        self.name = name
        from .mastotron import Mastotron
        
        if type(account_name_or_mastotron_obj) is Mastotron:
            self._tron = account_name_or_mastotron_obj
        elif type(account_name_or_mastotron_obj) is str:
            self._tron = Mastotron(account_name_or_mastotron_obj)
        else:
            raise Exception('Must provide either a string for an account name or a mastotron object.')

        # import networkdisk as nd
        # self._G = nd.sqlite.DiGraph(db=self.path, name='graphdb')
        from cog.torque import Graph
        from sqlitedict import SqliteDict
        self._g = Graph(self.name, cog_home=os.path.basename(self.path_g), cog_path_prefix=os.path.dirname(self.path_g))
        self._db = SqliteDict(self.path_db, autocommit=True)
        # self._db.create_or_load_namespace(f"{self.name}_ns")
        # self._db.create_table(f"{self.name}_db", f"{self.name}_ns")


    @property
    def path_g(self):
        return os.path.join(self._tron.path_acct, 'cog.graph')
    @property
    def path_db(self):
        return os.path.join(self._tron.path_acct, 'db.sqlitedict')

    @property
    def g(self): return self._g
    @property
    def db(self): return self._db

    def update(self, timeline_type='home'):
        for post in self._tron.iter_timeline(timeline_type=timeline_type):
            self.ingest_post(post)
        


def Node(uri, **kwargs):
    pass