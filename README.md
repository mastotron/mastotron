# Mastotron

A new interface to Mastodon, and other experiments in social media.

## Demo

https://user-images.githubusercontent.com/733853/217984843-15ae3fdf-2e40-4bca-b464-4f5b98871acf.mov



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

### Graphical use (normal)

Follow installation istructions above and then usage instructions inside the program.

(More documentation coming.)


### Use within python

```python
from mastotron import Tron
me = 'me@myserver.com'
posts = Tron().timeline(me)
```

## Contributing

Please do! You can report bugs and ask questions on the [issues](https://github.com/quadrismegistus/mastotron/issues) page.
