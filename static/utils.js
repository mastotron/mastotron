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