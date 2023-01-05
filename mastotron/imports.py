import os,sys; sys.path.insert(0,'..')
from functools import cached_property
from typing import Optional,Union,Dict,List
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
import numpy as np
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
warnings.filterwarnings('ignore')


path_data = os.path.expanduser('~/.mastotron')
path_env = os.path.join(path_data, 'config.json')
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







post_d = {'uri': 'https://sigmoid.social/users/maria_antoniak/statuses/109610274182309002',
 'poster_uri': 'https://sigmoid.social/@maria_antoniak',
 'url_local': 'https://zirk.us/@maria_antoniak@sigmoid.social/109610274271657669',
 'content': '<p>Playing with StoryGraph as an alternative to Goodreads or LibraryThing, and I\'m really interested in the various aspects you can attach to each book. For example, you can label whether a book has "lovable characters" or a "fast pace." I wonder how they came up with these labels?</p><p>Apparently I like slow-paced fiction that is "reflective, challenging, dark, adventurous, and mysterious."</p>',
 'html': '<div class="post origpost">\n<p>\n<div class="author"><img src="https://cdn.masto.host/zirkus/cache/accounts/avatars/109/309/672/173/687/430/original/c05334f193742528.png" /> <a href="https://zirk.us/@maria_antoniak@sigmoid.social" target="_blank">Maria Antoniak</a> (898 👥)</div> posted on 12/31/2022 at 20:54:12:\n</p>\n\n<p>Playing with StoryGraph as an alternative to Goodreads or LibraryThing, and I\'m really interested in the various aspects you can attach to each book. For example, you can label whether a book has "lovable characters" or a "fast pace." I wonder how they came up with these labels?</p><p>Apparently I like slow-paced fiction that is "reflective, challenging, dark, adventurous, and mysterious."</p>\n\n<center></center>\n\n<p>\n1 🗣\n|\n0 🔁\n|\n0 💙\n|\nPost ID: <a href="https://zirk.us/@maria_antoniak@sigmoid.social/109610274271657669" target="_blank">109610274271657669</a>\n</p>\n\n\n</div>',
 'is_boost': False,
 'is_reply': False,
 'in_boost_of__uri': '',
 'in_reply_to__uri': '',
 'timestamp': 1672520052,
 'score': 0.20498955988627823,
 'json_s':json.dumps({'scores':{
    'Simple': 1.0,
    'ExtendedSimple': 1.2599210498948732,
    'SimpleWeighted': 0.033351867298253506,
    'ExtendedSimpleWeighted': 0.042020719662370046,
 }})
}


poster_d={'uri': 'https://sigmoid.social/@maria_antoniak',
 'account_name': 'maria_antoniak@sigmoid.social',
 'display_name': 'Maria Antoniak',
 'url_local': 'https://zirk.us/@maria_antoniak@sigmoid.social',
 'desc': 'Postdoc at the Allen Institute for AI on the Semantic Scholar team.Researching #NLProc and #CulturalAnalytics, interested in narratives, healthcare, online communities, and measuring instabilities and biases.PhD from Cornell. Spent time at Twitter, Microsoft Research, Facebook, Pacific Northwest National Laboratory, UW Linguistics.I sometimes also share about books 📚, video games 🎮,  bicycles 🚲, Ukraine 🇺🇦, and gender inclusion in tech/academia 👩\u200d💻.',
 'html': '<div class="author"><img src="https://cdn.masto.host/zirkus/cache/accounts/avatars/109/309/672/173/687/430/original/c05334f193742528.png" /> <a href="https://zirk.us/@maria_antoniak@sigmoid.social" target="_blank">Maria Antoniak</a> (898 👥)<p>Postdoc at the Allen Institute for AI on the Semantic Scholar team.</p><p>Researching <a href="https://sigmoid.social/tags/NLProc" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>NLProc</span></a> and <a href="https://sigmoid.social/tags/CulturalAnalytics" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>CulturalAnalytics</span></a>, interested in narratives, healthcare, online communities, and measuring instabilities and biases.</p><p>PhD from Cornell. Spent time at Twitter, Microsoft Research, Facebook, Pacific Northwest National Laboratory, UW Linguistics.</p><p>I sometimes also share about books 📚, video games 🎮,  bicycles 🚲, Ukraine 🇺🇦, and gender inclusion in tech/academia 👩\u200d💻.</p></div>',
 'num_followers': 898,
 'num_following': 385,
 'is_bot': False,
 'is_org': False,
 'timestamp': 1667692800,
 'json_s':''}


mastodon_post_d = json.loads('{"id": 109625609742721263, "created_at": "2023-01-03 13:54:14.910000+00:00", "in_reply_to_id": null, "in_reply_to_account_id": null, "sensitive": false, "spoiler_text": "", "visibility": "unlisted", "language": "en", "uri": "https://zirk.us/users/TomUe/statuses/109625609742721263", "url": "https://zirk.us/@TomUe/109625609742721263", "replies_count": 0, "reblogs_count": 0, "favourites_count": 0, "edited_at": null, "favourited": false, "reblogged": false, "muted": false, "bookmarked": false, "content": "<p>RT @Atlantic_IMN@twitter.com</p><p>\\ud83d\\udce2Attention Atlantic-IMN students, don&#39;t forget to submit your abstract to the @DalCrossroads@twitter.com conference happening\\u00a0March 10-11\\u00a02023. Call for abstracts is open until Jan 6th!</p><p><a href=\\"https://dalcrossroads.com/\\" target=\\"_blank\\" rel=\\"nofollow noopener noreferrer\\"><span class=\\"invisible\\">https://</span><span class=\\"\\">dalcrossroads.com/</span><span class=\\"invisible\\"></span></a></p><p>\\ud83d\\udc26\\ud83d\\udd17: <a href=\\"https://twitter.com/Atlantic_IMN/status/1610259033457364997\\" target=\\"_blank\\" rel=\\"nofollow noopener noreferrer\\"><span class=\\"invisible\\">https://</span><span class=\\"ellipsis\\">twitter.com/Atlantic_IMN/statu</span><span class=\\"invisible\\">s/1610259033457364997</span></a></p>", "filtered": [], "reblog": null, "application": {"name": "Mastodon Twitter Crossposter", "website": "https://crossposter.masto.donte.com.br"}, "account": {"id": 109287998506018915, "username": "TomUe", "acct": "TomUe", "display_name": "Tom Ue", "locked": false, "bot": false, "discoverable": false, "group": false, "created_at": "2022-11-04 00:00:00+00:00", "note": "<p>Dr Tom Ue, FRHistS, researches and teaches courses at Dalhousie University.</p>", "url": "https://zirk.us/@TomUe", "avatar": "https://cdn.masto.host/zirkus/accounts/avatars/109/287/998/506/018/915/original/e0c2a970dae31855.jpg", "avatar_static": "https://cdn.masto.host/zirkus/accounts/avatars/109/287/998/506/018/915/original/e0c2a970dae31855.jpg", "header": "https://cdn.masto.host/zirkus/accounts/headers/109/287/998/506/018/915/original/0cb0ba61cb623a1a.jpeg", "header_static": "https://cdn.masto.host/zirkus/accounts/headers/109/287/998/506/018/915/original/0cb0ba61cb623a1a.jpeg", "followers_count": 222, "following_count": 213, "statuses_count": 757, "last_status_at": "2023-01-03 00:00:00", "noindex": false, "emojis": [], "fields": [{"name": "Twitter", "value": "@GissingGeorge", "verified_at": null}, {"name": "Web site", "value": "<a href=\\"https://dal.academia.edu/TomUe\\" target=\\"_blank\\" rel=\\"nofollow noopener noreferrer me\\"><span class=\\"invisible\\">https://</span><span class=\\"\\">dal.academia.edu/TomUe</span><span class=\\"invisible\\"></span></a>", "verified_at": null}, {"name": "Email", "value": "ue_tom@hotmail.com", "verified_at": null}]}, "media_attachments": [{"id": 109625609445328367, "type": "image", "url": "https://cdn.masto.host/zirkus/media_attachments/files/109/625/609/445/328/367/original/5a47ebfb99f6ef4f.jpg", "preview_url": "https://cdn.masto.host/zirkus/media_attachments/files/109/625/609/445/328/367/small/5a47ebfb99f6ef4f.jpg", "remote_url": null, "preview_remote_url": null, "text_url": null, "meta": {"original": {"width": 900, "height": 1200, "size": "900x1200", "aspect": 0.75}, "small": {"width": 416, "height": 554, "size": "416x554", "aspect": 0.7509025270758123}}, "description": null, "blurhash": "UTIZPA9FkC%M01IVRjxuS$ofV@j[Rjxtt7Rj"}], "mentions": [], "tags": [], "emojis": [], "card": {"url": "https://dalcrossroads.com/", "title": "Crossroads 2023", "description": "", "type": "link", "author_name": "dalcrossroads", "author_url": "https://dalcrossroads.com/author/dalcrossroads/", "provider_name": "Crossroads Interdisciplinary Health Research Conference", "provider_url": "http://dalcrossroads.com", "html": "", "width": 0, "height": 0, "image": null, "embed_url": "", "blurhash": null}, "poll": null}')
