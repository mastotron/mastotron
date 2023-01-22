REL_IS_LOCAL_FOR='is_local_for'
REL_IS_BOOST_OF='is_boost_of'
REL_IS_BOOST_OF='is_boost_of'
REL_IS_REPLY_TO='is_reply_to'
REL_READ_STATUS='rel_is_read'
NODE_READ_STATUS_IS_READ='read'
NODE_READ_STATUS_IS_UNREAD='unread'
REL_GRAPHTIME='when'


GRAPHTIME_ROUNDBY=10

LIMNODES=30
SCORE_TYPE = 'All'
LIM_TIMELINE=10


import os,sys; sys.path.insert(0,'..')
from pprint import pprint, pformat
import numpy as np
from functools import cached_property, lru_cache, total_ordering
cache = lru_cache(maxsize=None)
from typing import Optional,Union,Dict,List
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
import numpy as np
from mastodon.errors import MastodonNotFoundError, MastodonNetworkError
from mastodon import Mastodon, AttribAccessDict
from datetime import datetime, timedelta, timezone
import datetime as dt
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
import logging
import logging as log
logging.getLogger().setLevel(logging.INFO)  # choose your level here
from tqdm import tqdm
import mastodon






path_data = os.path.expanduser('~/.mastotron')
path_env = os.path.join(path_data, 'config.json')
path_db = os.path.join(path_data, 'db.sqlitedict')
path_tinydb = os.path.join(path_data, 'db.tinydb')
path_blitzdb = os.path.join(path_data, 'db.blitzdb')
path_cogdb = os.path.join(path_data, 'db.codgb')
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
from .htmlfmt import *
