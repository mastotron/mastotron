const path = require('path');
const request = require('request');
const kill = require('tree-kill');
const log = require('electron-log');  // https://www.npmjs.com/package/electron-log - npm i electron-log --save

let mainWindow = null;

// Figure out the Resources/ dir inside the electron app bundle.
let resourcesPath = process.resourcesPath;

// Figure out the Python executable path, based on the name 'app.py' built by
// Pyinstaller.  Note in the path below, the first 'app' refers to the path
// inside the Electron executable bundle, and the second 'app' is the name of
// the Python executable file.
let pythonExePath = path.join(process.resourcesPath, 'app', 'dist', process.platform === "win32" ? 'app.exe' : 'app');

// Record the process id of the Python flask child process so that we can kill it later.
let subpy;

const guessPackaged = () => {
    return require('fs').existsSync(pythonExePath)
}
log.info('pythonExePath', pythonExePath, 'packaged mode?', guessPackaged())

let numAttempts = 0
const maxAttemptsAllowed = 6
function checkFlask(cb) {  // cb is the function which will load the main window content etc.
    request('http://localhost:5000/', { json: true }, (err, res, body) => {
        // if (numAttempts < maxAttemptsAllowed) err = 'no flask'  // uncomment to simulate slow flask startup
        if (err) {
            if (numAttempts > 1)  // only warn after one retry, cos will usually need one retry anyway
                console.log(`Could not communicate with flask server ${err} 🤔 - its probably still starting up, waiting...`)
            numAttempts++
            if (numAttempts > maxAttemptsAllowed) {
                console.log(`Could not communicate with flask server ${err} 🆘 - gave up.`)
                // Call the callback even in the case of failure, so that always have something loaded in mainwindow render page
                if (cb)
                    cb()            }
            else
                setTimeout(function () {
                    checkFlask(cb)
                }, 500);
        }
        else if (res.statusCode != 200) {
            console.log(`Wrong response code from flask server ${res.statusCode} ${body} ⁉️⁉️⁉️ ⚠️`)
            if (cb)
                cb()
        }
        else {
            console.log('Communication with flask server is OK 🎉')
            // Call the callback even in the case of failure, so that always have something loaded in mainwindow render page
            if (cb)
                cb()
        }

    });
}

function runFlask() {
    // Launch Flask as a child process, wires up stdout and stderr so we can see them
    // in the electron main process console.  Remember Python needs to flush stdout

    // Actually no need to pass options and change cwd since that's all taken care of INTERNALLY inside the 
    // python app - it has the templates dir internally, which is unzipped into /tmp
    options = {}
    // options = {cwd: app_src_path }

    if (guessPackaged())
        subpy = require('child_process').spawn(pythonExePath, [], options);  // prod
    else
        subpy = require('child_process').spawn('python', [path.join(__dirname, '..', 'src-flask-server', 'app.py')]);  // dev

    console.log('Flask process id', subpy.pid)

    subpy.stdout.on('data', function (data) {
        let msg = `PYTHON stdout: ${data.toString('utf8')}`
        msg = msg.replace(/\n+$/, "")
        console.log(msg);
    });
    subpy.stderr.on('data', (data) => {
        let msg = `PYTHON stderr: ${data}`
        msg = msg.replace(/\n+$/, "")
        console.log(msg); // when error
    });
}

/*
normal quit
  window-all-closed
  before quit
file quit 
  before quit
*/
function killFlask(app) {
  
    if (subpy) {
    
    console.log('kill', subpy.pid)
    kill(subpy.pid, 'SIGKILL', function(err) {
        console.log('done killing flask')
        
        // App quit() logic
        
        mainWindow = null  
        app.quit();
          
                
    });

    }
    else {
        // App quit() logic
        
        mainWindow = null  
        app.quit();
          
    }

}
  

function closeMainWindow() {
    mainWindow.close();  // close window, which will then trigger 'window-all-closed'
}
function setMainWindow(_mainWindow) {
    mainWindow = _mainWindow
}
function getMainWindow(_mainWindow) {
    return mainWindow
}

exports.runFlask = runFlask
exports.checkFlask = checkFlask
exports.killFlask = killFlask
exports.closeMainWindow = closeMainWindow
exports.setMainWindow = setMainWindow
exports.getMainWindow = getMainWindow
