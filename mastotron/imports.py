import os,sys; sys.path.insert(0,'..')
from functools import cached_property
from typing import Optional,Union,Dict,List
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
import numpy as np
from mastodon.errors import MastodonNotFoundError
from mastodon import Mastodon, AttribAccessDict
from datetime import datetime, timedelta, timezone
from scipy.stats import gmean
from math import sqrt
import json
from pprint import pprint
import pandas as pd
from IPython.display import Markdown, display
def printm(x): display(Markdown(x))
import webbrowser,json, re
from collections import UserDict,UserList
def unhtml(x): 
    x = x.replace('<br>','\n')
    return re.sub(r'<.*?>', '', x).strip()
import networkx as nx
import pandas as pd
import warnings
from tinydb import Query, TinyDB
from sqlitedict import SqliteDict
warnings.filterwarnings('ignore')
import requests
from itertools import islice


path_data = os.path.expanduser('~/.mastotron')
path_env = os.path.join(path_data, 'config.json')
path_db = os.path.join(path_data, 'db.sqlitedict')
path_tinydb = os.path.join(path_data, 'db.tinydb')
app_name = 'mastotron'
API = None

from .exampledata import *
from .utils import *
from .mastotron import *
from .post import *
from .poster import *
from .postlist import *
from .postnet import *
from .db import *
from .graphdb import *

