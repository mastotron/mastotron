async function getRequest(url = '') {
    const response = await fetch(url, {
        method: 'GET',
        cache: 'no-cache'
    })
    return response.json()
}
document.addEventListener('DOMContentLoaded', function () {
    let url = document.location
    let route = "/flaskwebgui-keep-server-alive"
    let interval_request = 3 * 1000 //sec
    function keep_alive_server() {
        getRequest(url + route)
            // .then(data => console.log(data))
    }
    setInterval(keep_alive_server, interval_request);
})


var socket = io();
socket.on('connect', function() {
    socket.emit('my_event', {data: 'I\'m connected!'});
    console.log('connected!');
});


function popupwindow(url, title, w, h) {
var left = (screen.width/2)-(w/2);
var top = (screen.height/2)-(h/2);
return window.open(url, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
}



socket.on('logmsg', function(e){
    console.log('logmsg', e);
    msg = e['msg'];
    logmsg(msg);
});

function logmsg(x) {
    $.flash(x);
}

$(document).ready(function(){
    setTimeout(function() {
        $('#flash').fadeOut('slow');
    }, 2000); // <-- time in milliseconds
})
