
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
    arrows: {
      to: {
        enabled: true,
      }
    }
  }
};

var network = new vis.Network(container,data, options);


// SHOW
network.on("hoverNode", function (params) {
  // console.log("hoverNode Event:", params);
  node = params.node;
  node_d = nodes.get(node);
  console.log([node, node_d, nodes]);
  // if (node_d['node_type'] == 'post') {
    $('#tweet').html(node_d['html']);
    $('#tweet').show();
  // }
});

network.on("click", function (params) {
  node = this.getNodeAt(params.pointer.DOM);
  if (node == undefined) {
    $('#tweet').hide();
  }
});

function getdownstreamnodes(node) {
  nodes_downstream = network.getConnectedNodes(node, 'to');

  for (node2 of nodes_downstream) {
    nodes2_downstream = getdownstreamnodes(node2); //network.getConnectedNodes(node2);
    nodes_downstream.push(...nodes2_downstream);
  }
  nodes_downstream.push(node);
  return [...new Set(nodes_downstream)];
}

function delnodes(nl) {
  

  network.selectNodes(nl);
  network.deleteSelected();
}


network.on("doubleClick", function (params) {
  $('#tweet').hide();
  node = this.getNodeAt(params.pointer.DOM);
  if (node != undefined) {
    nlx = getdownstreamnodes(node);
    for(nid of nlx) {
      nodes.remove(nid);
    }
  } else {
    update_nodes();
  }
});

function add_node() {
  nodes.update([{id:nodes.length+1, label:'Hello'}]);
}

function update_nodes() {
  socket.emit('get_updates', {time:Date.now()})
}

socket.on('get_updates', function(data) {
  nodes.update(data.nodes);
  edges.update(data.edges);
});



$(document).ready(function(){update_nodes()});