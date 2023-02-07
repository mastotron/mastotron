document.addEventListener('DOMContentLoaded', function () {
    let url = document.location
    let route = "/flaskwebgui-keep-server-alive"
    let interval_request = 3 * 1000 //sec
    function keep_alive_server() {
        getRequest(url + route)
            // .then(data => console.log(data))
    }
    // setInterval(keep_alive_server, interval_request);
})


var socket = io();
socket.on('connect', function() {
    console.log('connected!');
});

socket.on('logmsg', function(e){
    console.log('logmsg', e);
    msg = e['msg'];
    logmsg(msg);
});

socket.on('logerror', function(e) { pb.error(e); })
socket.on('logsuccess', function(e) { pb.success(e); })
socket.on('loginfo', function(e) { pb.info(e); })










function popupwindow(url, title, w, h) {
    var left = (screen.width/2)-(w/2);
    var top = (screen.height/2)-(h/2);
    return window.open(url, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
}




function logmsg(x) {
    // console.log('logmsg',x);
    // $.flash(x);
    $('#logmsg').html(x);
}

// $(document).ready(function(){
//     setTimeout(function() {
//         $('#flash').fadeOut('slow');
//     }, 2000); // <-- time in milliseconds
// })


function get_datetime_str() {
    var m = new Date();
    var dateString =
        m.getUTCFullYear() + "-" +
        ("0" + (m.getUTCMonth()+1)).slice(-2) + "-" +
        ("0" + m.getUTCDate()).slice(-2) + " " +
        ("0" + m.getUTCHours()).slice(-2) + ":" +
        ("0" + m.getUTCMinutes()).slice(-2) + ":" +
        ("0" + m.getUTCSeconds()).slice(-2);
    return dateString;
}

function get_time_str() {
    var m = new Date();
    var dateString =
        ("0" + m.getUTCHours()).slice(-2) + ":" +
        ("0" + m.getUTCMinutes()).slice(-2) + ":" +
        ("0" + m.getUTCSeconds()).slice(-2);
    return dateString;
}



function moveNodeAnim(nodeId, finX, finY, duration) {
    if (!(nodeId in network.body.nodes)) { return; }
    let startPos = network.getPositions([nodeId])[nodeId];
    let startX = startPos.x;
    let startY = startPos.y;
    let startTime = performance.now();
    let _duration = duration || 1000;

    let move = (function () {
        if (!(nodeId in network.body.nodes)) { return; }
        let time = performance.now();
        let deltaTime = (time - startTime) / _duration;
        let currentX = startX + ((finX - startX) * deltaTime);
        let currentY = startY + ((finY - startY) * deltaTime);

        if (deltaTime >= 1) {
            network.moveNode(nodeId, finX, finY);
        } else
        {
            network.moveNode(nodeId, currentX, currentY);
            window.requestAnimationFrame(move);
        }

        nodes.update({'id':nodeId, 'x':currentX, 'y':currentY});
    });

    // if((startX!=finX) | (startY !=finY)) {
    move();
    // nodes.update({'id':nodeId, 'x':finX, 'y':finY});
    // }

}
function smudge(x, fac=100) {
    if (fac) {
        y = Math.random() * fac;
        if (Math.random() > .5) { y=-1*y; }
        return x + y;
    }
    return x;
}



function getIndexToIns(arr, num) {
    // Sort arr from least to greatest.
      let sortedArray = arr.sort((a, b) => a - b)
    //                  [40, 60].sort((a, b) => a - b)
    //                  [40, 60]
  
    // Compare num to each number in sortedArray
    // and find the index where num is less than or equal to 
    // a number in sortedArray.
      let index = sortedArray.findIndex((currentNum) => num <= currentNum)
    //            [40, 60].findIndex(40 => 50 <= 40) --> falsy
    //            [40, 60].findIndex(60 => 50 <= 60) --> truthy
    //            returns 1 because num would fit like so [40, 50, 60]
  
    // Return the correct index of num.
    // If num belongs at the end of sortedArray or if arr is empty 
    // return the length of arr.
      return index === -1 ? arr.length : index
  }

async function getRequest(url = '') {
    const response = await fetch(url, {
        method: 'GET',
        cache: 'no-cache'
    })
    return response.json()
}



function rescale_network() {
    console.log('rescaling')
    let yMin = Number.MAX_SAFE_INTEGER
    let yMax = Number.MIN_SAFE_INTEGER
    nodes.forEach(node => {
    // Using bounding box takes node height into account
    const boundingBox = network.getBoundingBox(node.id)
    if(boundingBox.top < yMin)
        yMin = boundingBox.top

    if(boundingBox.bottom > yMax)
        yMax = boundingBox.bottom
    })

    // Accounts for some node label clipping
    const heightOffset = 50

    // "Natural" aka 1.0 zoom height of the network
    const naturalHeight = yMax - yMin + heightOffset

    // container is a <div /> around the network with fixed px height;
    // the child network <canvas /> is height 100%
    container.style.height = naturalHeight + 'px'

    // Lets the network adjust to its new height inherited from container,
    // then fit() to zoom out as needed; note `autoResize` must be DISABLED for the network
    network.redraw()
    network.fit()

    // Sometimes the network grows too wide and fit() zooms out accordingly;
    // in this case, scale the height down and redraw/refit
    container.style.height = network.getScale() * naturalHeight + 'px'
    network.redraw()
    network.fit()
}


