// vars
var container = document.getElementById("mynetwork");
var nodes = new vis.DataSet();
var edges = new vis.DataSet();
var data = { nodes: nodes, edges: edges};
var options = {
  interaction:{
    hover: true,
    zoomSpeed: .1,
  },

  edges:{
    color: "gray",
    arrows: {
      to: {
        enabled: true,
        scaleFactor: .8,
      }
    }
  },

  nodes: {
    borderWidth: 1,
    size: 20,
    color: {
      border: "#222222",
      // background: "#666666",
      hover: "#777777"
    },
    font: { color: "#eeeeee" },
  },

  physics: {
    // wind: { x: 0, y: .25 }
  }
};

var network = new vis.Network(container,data, options);

var svg_str =
  '<svg xmlns="http://www.w3.org/2000/svg" width="390" height="65">' +
  '<rect x="0" y="0" width="100%" height="100%" fill="#7890A7" stroke-width="20" stroke="#ffffff" ></rect>' +
  '<foreignObject x="15" y="10" width="100%" height="100%">' +
  '<div xmlns="http://www.w3.org/1999/xhtml" style="font-size:40px">' +
  " <em>I</em> am" +
  '<span style="color:white; text-shadow:0 0 20px #000000;">' +
  " HTML in SVG!</span>" +
  "</div>" +
  "</foreignObject>" +
  "</svg>";

var svg_url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg_str);

console.log(svg_str);
console.log(svg_url);

// functions
function getdownstreamnodes(node) {
  nodes_downstream = network.getConnectedNodes(node, 'from');

  for (node2 of nodes_downstream) {
    nodes2_downstream = getdownstreamnodes(node2); //network.getConnectedNodes(node2);
    nodes_downstream.push(...nodes2_downstream);
  }
  nodes_downstream.push(node);
  return [...new Set(nodes_downstream)];
}

function del_nodes(node) {
  nlx = getdownstreamnodes(node);
  nlx.forEach(function(nx) { nodes.remove(nx); });
  socket.emit('mark_as_read', nlx);
}

function add_context(node) {
  socket.emit('add_context', node.id)
}

function add_node() {
  nodes.update([{id:nodes.length+1, label:'Hello'}]);
}



function get_node(params) {
  if ('node' in params) { 
    node = params.node;
  } else if (('nodes' in params) && (params.nodes.length>0)) {
    node = params.nodes[0];
  } else {
    try {
      node = this.getNodeAt(params.pointer.DOM);
    } catch (TypeError) {
      return undefined;
    }
  }
  console.log('node is',node);
  if (node != undefined) {
    node_d = nodes.get(node);
    return node_d;
  } else {
    return undefined;
  }
}


// SHOW
function shownode(params) {
  node_d = get_node(params);
  console.log('node = ', node_d);

  $('#tweet').html(node_d['html']);
  $('#tweet').show();
  
  offset = 20
  $('#tweet').offset(
    { top: params.event.y + offset, 
      left: params.event.x + offset
    });
}

network.on("hoverNode", function (params) {
  shownode(params);
});



network.on("click", function (params) {
  node_d = get_node(params);
  if (node_d == undefined) {
    $('#tweet').hide();
  } else {
    shownode(params);
    // window.open(node_d.id, '_blank');
  }
});

network.on("doubleClick", function (params) {
  $('#tweet').hide();
  console.log(params);
  node_d = get_node(params);
  if (node_d != undefined) {
    del_nodes(node_d.id);
    // add_context(node_d);
    // window.open(node_d.id, '_blank');
  } else {
    update_nodes();
  }
});

network.on("oncontext", function (params) {
  $('#tweet').hide();
  params.event.preventDefault();
  console.log(params);
  node_d = get_node(params);
  if (node_d != undefined) {
    // del_nodes(node_d.id);
    window.open(node_d.id, '_blank');
  }
});



// socket events


function update_nodes() {
  console.log('update_nodes()');
  logmsg('refreshing');
  socket.emit('get_updates', {time:Date.now()})
}

socket.on('get_updates', function(data) {
  console.log('get_updates', data);
  nodes.update(data.nodes);
  edges.update(data.edges);
});

function startnet() {
  console.log('starting network!');
  update_nodes();
}

// start
$(document).ready(function(){  
  startnet();

  // setTimeout(function() { update_nodes(); }, 1000);
  socket.emit('start_updates');
  
  setInterval(function() { socket.emit('get_pushes'); }, 1 * 1000);
  setInterval(function() { socket.emit('get_updates'); }, 30 * 1000);


  // var handle = $( "#custom-handle" );
  // $( "#slider" ).slider({
  //   create: function() {
  //     handle.text( $( this ).slider( "value" ) );
  //   },
  //   slide: function( event, ui ) {
  //     handle.text( ui.value );
  //   }
  // });

});

