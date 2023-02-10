PORT=1789
HOST='localhost'
REL_IS_LOCAL_FOR='is_local_for'
REL_IS_BOOST_OF='is_boost_of'
REL_IS_BOOST_OF='is_boost_of'
REL_IS_REPLY_TO='is_reply_to'
REL_HAS_ID = 'has_id'
REL_TO_ID = 'to_id'
REL_READ_STATUS='rel_is_read'
NODE_READ_STATUS_IS_READ='read'
NODE_READ_STATUS_IS_UNREAD='unread'
REL_GRAPHTIME='when'


BLUR_MINUTES=5   # 1 minutes grace period / blur

LIMNODES=20
SCORE_TYPE = 'All'
LIM_TIMELINE=20
LIM_CONVO=3


import os,sys; sys.path.insert(0,'..')
FORK_AVAILABLE=False
os.environ['FORK_AVAILABLE']=str(FORK_AVAILABLE)
path_imports = path_self = os.path.realpath(__file__)
path_gui = os.path.abspath(os.path.join(path_imports,'..','gui'))
path_code = os.path.abspath(os.path.join(path_imports,'..','..'))
path_web = path_gui
path_static = os.path.join(path_web,'static')
path_templates = os.path.join(path_web,'templates')

from pprint import pprint, pformat
import textwrap,random
import numpy as np
import click
from functools import cached_property, lru_cache, total_ordering
cache = lru_cache(maxsize=None)
from typing import Optional,Union,Dict,List
import numpy as np
from mastodon.errors import MastodonNotFoundError, MastodonNetworkError
from mastodon.utility import AttribAccessDict
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
from collections import UserDict,UserList,defaultdict
def unhtml(x): 
    x = x.replace('<br>','\n')
    return re.sub(r'<.*?>', '', x).strip()
import networkx as nx
import pandas as pd
import warnings
from sqlitedict import SqliteDict
warnings.filterwarnings('ignore')
import requests
from itertools import islice
import logging
import logging as log
logging.getLogger().setLevel(logging.INFO)  # choose your level here
from tqdm import tqdm
import mastodon
from multiprocessing.pool import ThreadPool




path_data = os.path.expanduser('~/.mastotron')
path_srvr = os.path.join(path_data, 'db.webview')
path_env = os.path.join(path_data, 'config.json')
path_db = os.path.join(path_data, 'db.sqlitedict')
path_tinydb = os.path.join(path_data, 'db.tinydb')
path_blitzdb = os.path.join(path_data, 'db.blitzdb')
path_cogdb = os.path.join(path_data, 'db.codgb')
app_name = 'mastotron'
API = None

from .utils import *
from .mastotron import *
from .post import *
from .poster import *
from .postlist import *
from .postnet import *
from .db import *
from .graphdb import *
from .htmlfmt import *
