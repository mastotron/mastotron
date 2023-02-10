# Mastotron

A new interface to Mastodon, and other experiments in social media.

## Demo

[![Mastotron](https://www.dropbox.com/s/1ubsu22mpqjemek/Matotron-v1b.png?raw=1)](https://www.dropbox.com/s/rme46j0xl3qmeaw/Mastotron-v1b.mov?raw=1)

https://www.dropbox.com/s/rme46j0xl3qmeaw/Mastotron-v1b.mov?raw=1

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

### Use normally

Follow installation istructions above and then usage instructions inside the program.

(More documentation coming.)


### Use in jupyter/python

```python
from mastotron import Tron
me = 'me@myserver.com'
posts = Tron().timeline(me)
```

## Contributing

Please!