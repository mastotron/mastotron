// A way of safely requiring nodejs stuff in the render process
// rather than opening up safety problems with contextIsolation: true
// We can keep contextIsolation: false in src/index.js and still get access here.
// See https://stackoverflow.com/questions/54544519/electron-require-is-not-defined
window.ipcRenderer = require('electron').ipcRenderer;