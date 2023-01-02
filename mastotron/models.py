from .imports import *

# from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

# class dbPoster(SQLModel, table=True):
#     uri: str = Field(default=None, primary_key=True)
#     account_name: str
#     display_name: str
#     desc: str
#     num_followers: int
#     num_following: int
#     is_bot: bool
#     is_org: bool
#     timestamp: int
#     json_s: str
#     posts: List['dbPost'] = Relationship(back_populates='poster')

# class dbPost(SQLModel, table=True):
#     uri: str = Field(default=None, primary_key=True)
#     poster_uri: str = Field(default=None, foreign_key="dbposter.uri")
#     poster: dbPoster = Relationship(back_populates='posts')
#     url_local: str
#     content: str
#     is_boost: bool
#     is_reply: bool
#     in_boost_of__uri: str = Field(default=None, foreign_key="dbpost.uri")
#     # in_boost_of: Optional['dbPost'] = Relationship()
#     in_reply_to__uri: str = Field(default=None, foreign_key="dbpost.uri")
#     # in_reply_to: Optional['dbPost'] = Relationship()

#     timestamp: int
#     score: float
#     # scores: Dict[str,float]
#     json_s: str


#     def hello(self):
#         print(self.uri,'!!!')



def connect():
    from mastotron import path_data
    engine = create_engine(f'sqlite:///{path_data}/testdb.sqlite')
    SQLModel.metadata.create_all(engine)
    return Session(engine)




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
#  'scores':{
#     'Simple': 1.0,
#     'ExtendedSimple': 1.2599210498948732,
#     'SimpleWeighted': 0.033351867298253506,
#     'ExtendedSimpleWeighted': 0.042020719662370046,
#  },
 'score': 0.20498955988627823,
#  'timeline_type': 'home',
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



