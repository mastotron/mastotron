# Mastotron

<p align="center">
<img src="mastotron/gui/static/dalle3-transp-small.png" alt="mastotron"><br/>
<i>Mastotron mascot by DALL-E</i>
</p>

Mastotron is a different interface to [Mastodon](github.com/mastodon/mastodon), replacing the mindless "feed" of most social media with a network map of conversations and recent and popular posts.

## Demo

### Pictures

<div id="image-table">
    <table>
	    <tr>
    	    <td style="padding:10px">
        	    <img src="https://user-images.githubusercontent.com/733853/218314646-69c8dd75-adae-4bd0-ab13-fd10b9c6318c.png"/>
      	    </td>
            <td style="padding:10px">
            	<img src="https://user-images.githubusercontent.com/733853/218312970-1fefc050-f274-44b5-aece-2d25fb77ba3b.png"/>
            </td>
        </tr>
	    <tr>
    	    <td style="padding:10px">
        	    <img src="https://user-images.githubusercontent.com/733853/218314426-b14636b9-5560-4c41-a46e-a68849b1925b.png"/>
      	    </td>
            <td style="padding:10px">
            	<img src="https://user-images.githubusercontent.com/733853/218312943-9e6413e2-ea79-4e63-97af-1df09b916cbe.png"/>
            </td>
        </tr>
    </table>
</div>

### Video

https://user-images.githubusercontent.com/733853/217984843-15ae3fdf-2e40-4bca-b464-4f5b98871acf.mov



## Installation

Right now Mastodon is a desktop application rather than website you can navigate. This is primarily so that the (already minimal) data it collects stays entirely on your hardware rather than on a server somewhere. That makes it safer and free to run: no server costs, no risk of hacking, etc. 

Maybe one day we could make a mobile app, though the graphical interface would probably need to be redesigned.

### MacOS

Thankfully double-click installation is working here, though you'll need to convince MacOS to open an app from an "unidentified developer" ([more info](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac)). 

1. [Download the latest zip file release (`Mastotron-macos.zip`)](https://github.com/quadrismegistus/mastotron/releases/download/v1.0.0/Mastotron-macos.zip)
2. Unzip the file to reveal `Mastotron.app`
3. Hold control (⌃) and click the file; click "Open" in the menu; then click "open" again at the prompt
    * If this doesn't work, try going to System Preferences->Security and "allow" it to run.
4. Wait for the window to appear (this is slow; could take a minute+)

### Linux

As of Release v1, the builtin mini browser isn't working for
linux users, but it works just as fine in your own browser
with mastotron running in the background:

```
# install (do just once)
pip3 install -U git+https://github.com/quadrismegistus/mastotron

# run
mastotron --bg
```

Then, in your favorite browser, navigate to [http://localhost:1789](http://localhost:1789).

### Windows

... Coming soon. For now, try following instructions above for Linux.

## Usage

### Graphical use (normal)

* Hover over a node to read the post.
* Right-click it or press (C) to load its replies.
* Press (D) to dismiss it or "mark it as read".
    * Crucially, a dismissed post will never re-appear. This is good! It means you can "mark as read" a post and by never seeing it again you can trust that more of your timeline is new content.
* Press (N) for next batch in queue.
* Press (L) for latest in queue.
* Press (R) to query mastodon to find 3 new posts not in graph or queue.
* Press (Cmd+R) to query mastodon to find 10 new posts not in graph or queue.
* Press (P) to pause/play the animation.

### Use within python

```python
from mastotron import Tron
me = 'me@myserver.com'
posts = Tron().timeline(me)
```

## What is happening?

There are a few different processes happening once you boot up:

1. The backend (written in python) makes sure you're logged in and the account name is set locally: if not, it redirects you to the login page.
2. Once the frontend (written in javascript) boots up, it sends a request to the backend for `N` posts (set by `#` button on lefthand side)
3. Once the backend hears from the frontend, it starts up a few processes:
    * A separate 'listener' thread is created which connects to your mastodon server's Streaming API for real-time brand-new push updates
    * A separate 'crawler' thread which, after a 60 second delay, will request the last 10 posts from your mastodon server
        * This is a separate thread so your communication with the mastodon server about the latest posts is kept separate from the normal request operations
    * Then the next, normal request operation is performed
4. Whenever the backend is asked for updates, it starts iterating backwards over 5-minute intervals, starting from now and rounding down (if it's 5:43pm, it starts at 5:35-5:40, then 5:30-35, and so n)
    * For each of these 5 minute interval, it either...
        * requests your mastodon account's server for any timeline post in that 5-minute interval; then caches the result
        * or, if that 5-minute interval was requested previously and cached, it returns the result it's cached
    * As these results come in, it pushes each one immediately to the frontend
5. Whenever the frontend receives a new post from the backend, it thinks through these steps:
    * Do I have as many nodes in the graph right now as I want to (set by `#` on lefthand side)?
        * No? then display this post immediately on the graph.
        * Yes? then proceed to next step
    * Is this a special kind of update? 
        * Is this a  'force push' update? (e.g. when replies are requested via right-click or (C)
            * then add it directly to the graph, booting off the least recent one if necessary to stay under the `#` limit
        * Is this a 'background' update? (e.g. from the crawler process above)
            * then proceed to next step
    * Otherwise, add to the "queue" stored on the frontend
        * (For now, this queue stores a maximum 200 posts; the most recent 200 sent from the backend are preserved)
6. In addition, every X seconds (set by the `⟤` button on the left-hand side), `turnover_nodes()` occurs
    * This just brings in the latest addition to the queue into the graph, booting back into the queue the least recent post on the graph
        * Crucially, this means that you are not querying your mastodon server every X seconds: it's just a front-end animation
    * When active, tou can turn this animatin off by pressing the `■` on the left-hand side; when paused you can re-activate it by pressing the `▶` key
7. Finally, every 60 seconds an update is requested from the server, which will follow the logic of step 4

Now that I've typed this all out I can see it's a bit over-complicated. I've created an [issue here](https://github.com/quadrismegistus/mastotron/issues/20) if you have thoughts on how to simplify it.

## Technical details

### Frontend

Code [here](https://github.com/quadrismegistus/mastotron/blob/main/mastotron/gui/static/postnet.js) mainly. It's my (simple but probably clunky) javascript adaptation of [https://github.com/visjs](https://github.com/visjs) to display the nodes and edges and labels and images of the posts.

### Backend

Code [here](https://github.com/quadrismegistus/mastotron/blob/main/mastotron/gui/app.py). Running [flask](https://github.com/pallets/flask) and communicating with the front-end via HTTP (only to serve the initial HTML and CSS and javascript) and subsequently via realtime web sockets (through [flask-socketio](https://github.com/miguelgrinberg/Flask-SocketIO)).


### Backend to the backend

Code [here](https://github.com/quadrismegistus/mastotron/blob/main/mastotron/mastotron.py) mainly. This interfaces with [mastodon.py](https://github.com/halcy/Mastodon.py) (which is a python implementation of the [Mastodon API](https://docs.joinmastodon.org/api/)) to read and cache posts from your timeline. Mastotron's only innovation here is laid out in step 4 of the section above, which is to query for 5 minute intervals and cache the results; this ensures minimal requests to your mastodon server.

### Backend to the backend to the backend 

Code [here](https://github.com/quadrismegistus/mastotron/blob/main/mastotron/post.py) mainly.

Mastodon is weird. Sorry. I'm new to it. The account and post URIs it gives you are relative to your local server but there is no simple way to translate between URIs and ones on the server for the account it posted from. This is a problem for understanding relations between posts across URIs:
* If post-A-from-server-X is a reply to post-B-from-server-Y, then in order to load _other_ replies to post-B-on-server-Y (such as post-C-from-server-Z) you need to [ask server Y for the "context" of post B](https://docs.joinmastodon.org/entities/Context/).
* Server Y will then give you a bunch of IDs _will make sense only to server Y_: 
    * Server X (where our user is located) has no idea what they mean!
    * Server Z (where the author of the reply is located) _also_ has no idea what they mean!

Mastotron tries hard to figure all this out by storing post URLs and their relations in a mini graph database known as [cogdb](https://github.com/arun1729/cog). Here a node is any post URL, on any server, which may have relations with other post URLs including `REL_IS_LOCAL_FOR` (is a local URL for the URL of the post), `REL_IS_BOOST_OF`, and `REL_IS_REPLY_TO` (self-explanatory).

That way it's possible to ask of any post, what posts have replied to me, even if the replies are expressed in IDs across different servers. (It does that in graph-speak by asking what incoming edges both the local URL of a post and its URL on its own server have.) Which posts have boosted me? And so on. All those facts are discovered in a few different ways each of which returns IDs from different servers (a post which is a reply will give you a reply ID from the timeline server, but the context API will give you an ID from the poster's server, etc). Because of that, I thought it'd be better to store those facts in a graph database so you can ask questions like this with minimal querying of mastodon.

## Contributing

Please do! You can report bugs and ask questions on the [issues](https://github.com/quadrismegistus/mastotron/issues) page. Pull requests are always welcome and encouraged.

I'm going to move this repository to an organization to further encourage outside contributions. I'm thrilled Mastotron has received interest and I'd love for it to be a collective open source endeavor as much as posssible!
