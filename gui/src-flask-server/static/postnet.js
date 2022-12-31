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
        scaleFactor: .6,
      }
    }
  },

  nodes: {
    borderWidth: 1,
    size: 30,
    color: {
      border: "#222222",
      // background: "#666666",
      hover: "#777777"
    },
    font: { color: "#eeeeee" },
  },
};

var network = new vis.Network(container,data, options);


// functions
function getdownstreamnodes(node) {
  nodes_downstream = network.getConnectedNodes(node, 'to');

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
network.on("hoverNode", function (params) {
  node_d = get_node(params);
  console.log('node = ', node_d);

  $('#tweet').html(node_d['html']);
  $('#tweet').show();
  
  offset = 20
  $('#tweet').offset(
    { top: params.event.y + offset, 
      left: params.event.x + offset
    });
  
  // }
});



network.on("click", function (params) {
  node = this.getNodeAt(params.pointer.DOM);
  if (node == undefined) {
    $('#tweet').hide();
  }
});

network.on("doubleClick", function (params) {
  $('#tweet').hide();
  console.log(params);
  node_d = get_node(params);
  if (node_d != undefined) {
    del_nodes(node_d.id);
    // window.open(node_d.url, '_blank');
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
    del_nodes(node_d.id);
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
  setTimeout(function() {
    update_nodes();
  }, 1000);
  
  setInterval(function() {
    update_nodes();
  }, 30 * 1000);
// });

  var handle = $( "#custom-handle" );
  $( "#slider" ).slider({
    create: function() {
      handle.text( $( this ).slider( "value" ) );
    },
    slide: function( event, ui ) {
      handle.text( ui.value );
    }
  });
});

