# mastotron

A new interface to mastodon and other new experiments in social media.

## Demo

...

## Installation

### MacOS

1. [Download the latest zip file release (`Mastotron-macos.zip`)](https://github.com/quadrismegistus/mastotron/releases/download/v1.0.0/Mastotron-macos.zip)
2. Unzip the file to reveal `Mastotron.app`
3. Hold control (⌃) and click the file
4. Click "Open" in the menu, then click "open" again at the prompt ([more info](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac))
5. Wait for the window to appear

### Linux

1. [Download the latest zip file release (`Mastotron-linux.zip`)](https://github.com/quadrismegistus/mastotron/releases/download/v1.0.0/Mastotron-linux.zip)
2. Unzip the file to reveal `MastotronApp`
3. Double-click this and wait for the window to appear


### Windows

... Coming soon. For now, follow instruction for Python.

### Python

1. First install python. 
2. In a terminal type: `pip install git+https://github.com/quadrismegistus/mastotron`
3. In a terminal type: `mastotron`


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
