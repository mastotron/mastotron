# mastotron

Experiments rewiring social media

## Demo

...

## Installation

### MacOS

1. [Download the latest zip file release (`Mastotron-macos.zip`)](https://github.com/quadrismegistus/mastotron/releases/download/v1.0.0/Mastotron-macos.zip)
2. Unzip the file to reveal `Mastotron.app`
3. Double-click this and wait for a terminal to appear
4. Wait 30-60sec here until a text-art elephant appears with a URL
5. Paste this URL (auto-copied to clipboard in step 4) into your browser

### Linux

1. Download the latest zip file release (`Mastotron-linux.zip`).
2. Unzip the file to reveal `MastotronApp`
3. Double-click this and wait for a terminal to appear
4. Wait 30-60sec here until a text-art elephant appears with a URL
5. Paste this URL (auto-copied to clipboard in step 4) into your browser


### Windows

... Coming soon. For now, follow instruction for Python.

### Python

1. First install python. 
2. In a terminal type: `pip install mastotron`
3. In a terminal type: `mastotron`
4. Wait 30-60sec here until a text-art elephant appears with a URL
5. Paste this URL (auto-copied to clipboard in step 4) into your browser



## Usage

...


## Development


### Use in jupyter/python

```python
# load the class
from mastotron import Tron
# instantiate
tron = Tron()
# get latest posts; will guide through auth
posts = tron.timeline('myaccount@mastodonserver.com')
```
