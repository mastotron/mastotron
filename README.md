# mastotron

```python
# load the class
from mastotron import Mastotron, Post

# instantiate; will guide through auth
tron = Mastotron()

# Get a post by id on your server
post = Post(id=109566222383974657)
post
```





<div class="post origpost" style="border:1px solid orange;padding:0 1em;">
<p>
<a href="https://mstdn.science/@RebeccaRHelm">RebeccaRHelm@mstdn.science</a> (1,157 👥) <a href="https://mstdn.science/@RebeccaRHelm/109566221656683705">wrote</a> on 12/24/2022 at 02:11:04:
</p>

<p>EXTREMELY RARE footage of the elusive box jellyfish Chirodectes. Larger than a soccer ball, this jelly is a true ocean mystery, and this video is one of the only in existence, filmed off the coast of Papua New Guinea in 2021.<br>📽️Scuba Ventures Kavieng bit.ly/3FE29tL</p>

<center><a href="https://cdn.masto.host/zirkus/cache/media_attachments/files/109/566/221/923/419/468/small/f0a9cc7c3910417e.png"><img src="https://cdn.masto.host/zirkus/cache/media_attachments/files/109/566/221/923/419/468/small/f0a9cc7c3910417e.png" /></a></center>

<p>
10 🗣
&nbsp; | &nbsp; 
71 🔁
&nbsp; | &nbsp;
4 💙
&nbsp; | &nbsp;
Post ID: 109566222383974657
</p>
</div>





```python
# These will show reposts
post = Post(id=109565672404848243)
post
```





<div class="post reblog" style="border:1px solid blue; padding: 0 1em;">
<p>
<a href="https://zirk.us/@accommodatingly">accommodatingly</a> (287 👥) reposted at 12/23/2022 at 23:51:23:
</p>


<div class="post origpost" style="border:1px solid orange;padding:0 1em;">
<p>
<a href="https://strangeobject.space/@esther">esther@strangeobject.space</a> (1,367 👥) <a href="https://strangeobject.space/@esther/109563512148655648">wrote</a> on 12/23/2022 at 14:42:00:
</p>

<p>Thinking of all the queer folks who have to spend the holidays with abusive, unaccepting, unsupportive, or “well meaning” but careless relatives. It’s an especially dark time for many who can’t escape those situations because they’re minors, financially dependent, or under emotional pressure to attend.</p><p>If you’re out there, struggling, and need a friendly voice, feel free to drop a DM. I’m happy to be your trans goth aunt for a bit.</p><p><a href="https://strangeobject.space/tags/queer" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>queer</span></a> <a href="https://strangeobject.space/tags/trans" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>trans</span></a> <a href="https://strangeobject.space/tags/holidays" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>holidays</span></a> <a href="https://strangeobject.space/tags/support" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>support</span></a></p>

<center></center>

<p>
12 🗣
&nbsp; | &nbsp; 
60 🔁
&nbsp; | &nbsp;
4 💙
&nbsp; | &nbsp;
Post ID: 109563512620764058
</p>


</div>

<br/>

</div>





```python
# And replies
post = Post(id=109564529870067074)
post
```





<div class="post origpost" style="border:1px solid orange;padding:0 1em;">
<p>
<a href="https://zirk.us/@heuser">heuser</a> (235 👥) <a href="https://zirk.us/@heuser/109564529870067074">wrote</a> on 12/23/2022 at 19:00:50:
</p>

<p>Unexpected challenge: there are very few likes on tweets in my mastodon timeline. (step that up pls everyone thx.) So it&#39;s hard to sort the tweets using that metric.</p>

<center></center>

<p>
1 🗣
&nbsp; | &nbsp; 
0 🔁
&nbsp; | &nbsp;
2 💙
&nbsp; | &nbsp;
Post ID: 109564529870067074
</p>

<p><b><i>... in reply to:</i></b></p> 
<div class="post origpost" style="border:1px solid orange;padding:0 1em;">
<p>
<a href="https://zirk.us/@heuser">heuser</a> (235 👥) <a href="https://zirk.us/@heuser/109564459673004810">wrote</a> on 12/23/2022 at 18:42:58:
</p>

<p>Experimenting with making an &quot;algorithm&quot; to sort a user&#39;s feed using python and mastodon.py. This tweet was sent from a jupyter notebook.</p>

<center></center>

<p>
1 🗣
&nbsp; | &nbsp; 
1 🔁
&nbsp; | &nbsp;
3 💙
&nbsp; | &nbsp;
Post ID: 109564459673004810
</p>


</div>
<br/> 
</div>





```python
# Get scores for a post 
# (adapted from https://github.com/hodgesmr/mastodon_digest)
post.scores()
```




{'Simple': 1.7320508075688774,
'ExtendedSimple': 1.8171205928321397,
'SimpleWeighted': 0.11274690420042434,
'ExtendedSimpleWeighted': 0.11828447555082267,
'All': 0.4526308886948211}




```python
# Get top posts by score
top_posts = sorted(
tron.latest_posts(max_posts=100),
key=lambda post: -post.score()
)

# top post by engagement
top_posts[0]
```





<div class="post reblog" style="border:1px solid blue; padding: 0 1em;">
<p>
<a href="https://zirk.us/@ecourtem">ecourtem</a> (346 👥) reposted at 12/23/2022 at 14:53:21:
</p>


<div class="post origpost" style="border:1px solid orange;padding:0 1em;">
<p>
<a href="https://mstdn.social/@lolennui">lolennui@mstdn.social</a> (5,061 👥) <a href="https://mstdn.social/@lolennui/109560660969613944">wrote</a> on 12/23/2022 at 02:36:55:
</p>

<p>Every gen X person read a terrifying Stephen King book when they were 9</p>

<center></center>

<p>
55 🗣
&nbsp; | &nbsp; 
33 🔁
&nbsp; | &nbsp;
1 💙
&nbsp; | &nbsp;
Post ID: 109560661039545409
</p>


</div>

<br/>

</div>



