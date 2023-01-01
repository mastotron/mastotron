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
    d = db

    def update(self, timeline_type='home', max_posts=100, hours_ago=24):
        for post in self._tron.iter_timeline(
                timeline_type=timeline_type,
                max_posts=max_posts,
                hours_ago=hours_ago):
            self.ingest_post(post, timeline_type=timeline_type)

    def ingest_post(self, post, force=False, **extra):
        if force or not post.uri in self.d:
            print(f'>> ingesting: {post.uri}')
            self.d[post.uri] = {**post.data, **extra}
            self.d[post.author.uri] = post.author.data
            self.g.put(post.author.uri,'posted',post.uri)