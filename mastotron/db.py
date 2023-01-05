from .imports import *
from sqlmodel import Session, SQLModel, create_engine

class TronDB:
    def __init__(self, name='testdb'):
        self.name=name
        self.engine = create_engine(f'sqlite:///{self.path}')
        SQLModel.metadata.create_all(self.engine)
    
    @property
    def path(self):
        from mastotron import path_data
        return os.path.join(path_data, f'{self.name}.sqlite')
    
    def connect(self): return Session(self.engine)
    def __enter__(self): return self.connect()
    def __exit__(self,*x,**y): pass
    
    