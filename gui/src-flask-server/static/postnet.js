// vars
var MODE = 'default';
var SCORE_TYPE = 'ExtendedSimple';
var darkbgcolor = 'rgb(20,20,23)'; //#28282B';
var lightbgcolor = '#eeeeee';
var lighttweetbg = 'white';
var darktweetbg = 'rgba(30,30,33, 0.9)'; //#28282B';
var darktxtcolor = 'white';
var lighttxtcolor = 'black';
var darkimg = "/static/dark-mode-6682-inv.png";
var lightimg = "/static/dark-mode-6682.png";
var limnodesgraph = 50;
if (DARKMODE==1) { 
  var txtcolor = darktxtcolor; 
} else { 
  var txtcolor = lighttxtcolor;  
}


// start containers
var container = document.getElementById("postnetviz");
var nodes = new vis.DataSet();
var edges = new vis.DataSet();
var data = { nodes: nodes, edges: edges};
var options = {
  interaction:{
    hover: true,
    zoomSpeed: .1,
  },

  edges:{
    color: "silver",
    arrows: {
      to: {
        enabled: true,
        scaleFactor: .6,
      },
      middle: { enabled: false },
      from: { 
        enabled: false,
        scaleFactor: .4,
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
    font: { 
      color: txtcolor
    },
  },

  physics: {
    // wind: { x: 0, y: .25 }
  },
};

var network = new vis.Network(container, data, options);

// FUNCTIONS

function startnet() {
  console.log('starting network!');
  socket.emit('start_updates');
  request_updates();
}

function iter_edges() { return Object.values(network.body.edges); }
function iter_nodes() { return Object.values(network.body.nodes); }


// UI functions



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
  // console.log('node is',node);
  if (node != undefined) {
    node_d = nodes.get(node);
    return node_d;
  } else {
    return undefined;
  }
}


// SHOW
function show_status_div(params) {
  node_d = get_node(params);
  node_pos = network.getPosition(node_d.id);
  node_pos_web = network.canvasToDOM(node_pos);
  _offset = 0;
  $('#tweet').html(node_d['html']);  
  x = node_pos_web['x'];
  y = node_pos_web['y'];
  $('#tweet').offset(
    { top: y + _offset, 
      left: x + _offset
    });
  $('#tweet').show();
}

function hide_status_div() { $('#tweet').hide(); }

function nodes_to_ids(_nodes) {
  _nodes_ids = [];
  _nodes.forEach(function(_node) {
    _nodes_ids.push(_node.id); 
  })
  return _nodes_ids;
}


function getdownstreamnodes(node_id, recurse=2) {
  nodes_downstream_ids = network.getConnectedNodes(
    node_id,
    direction=undefined
  );
  if (recurse > 0) {
    for (node2 of nodes_downstream_ids) {
      nodes_downstream_ids.push(
        ...getdownstreamnodes(
          node2,
          recurse=recurse-1
        )
      );
    }
  }
  nodes_downstream_ids.push(node_id);
  return [...new Set(nodes_downstream_ids)];
}

function del_nodes(node_id) {
  node_ids_to_del = getdownstreamnodes(node_id);
  console.log('mark_as_read',node_ids_to_del);
  socket.emit('mark_as_read', node_ids_to_del);
  nodes.remove(node_ids_to_del);
  size_nodes();
}

function add_context(node_id) {
  console.log('getting context for:',node_id);
  socket.emit('add_context', node_id)
}



// socket events




function update_nodes(data) {
  lim = limnodesgraph;
  nodes.update(data.nodes);
  edges.update(data.edges);
  style_edges();
  size_nodes();
}




function style_edges() {
  for (edge of iter_edges()) {
    edge_d = edges.get(edge.id);
    if (edge_d.edge_type=='in_boost_of') {
      edge.options.arrows.to.type = 'circle';
      edge.options.arrows.from.type = 'circle';
      // edge.options.arrows.to.enabled = true;
      // edge.options.arrows.from.enabled = false;
    } else {
      edge.options.arrows.to.type = 'arrow';
      edge.options.arrows.from.type = 'bar';
      // edge.options.arrows.to.enabled = true;
      // edge.options.arrows.from.enabled = false;
    }
  }
}

function change_node_color(color) {
  for (node of iter_nodes()) {
    node_d = nodes.get(node.id);
    if (node_d != null) {
      node_d.font = {'color':color}
      nodes.update(node_d);
    }
  }
}

function get_nodes_d(node_obj=true) {
  d={};
  for (n of iter_nodes()) {
    if (node_obj) { nobj = n; } else { nobj = nodes.get(n.id); }
    d[n.id] = nobj;
  }
  return d;
}


function get_node_scores(score_type=SCORE_TYPE, log = false) {
  // get scores
  scores = {};
  for (node of iter_nodes()) { 
    node_d = nodes.get(node.id);
    if (node_d != null) {
      score = node_d.scores[score_type]+1;
      if (log) { score = Math.log10(score); }
      scores[node.id] = score;
    }
  }
  return scores;
}

function scaleBetween(unscaledNum, minAllowed, maxAllowed, min, max) {
  return (maxAllowed - minAllowed) * (unscaledNum - min) / (max - min) + minAllowed;
}

function size_nodes(max_size=40, min_size=20, score_type=SCORE_TYPE) {  
  scores = get_node_scores();
  max_score = Math.max(...Object.values(scores));
  min_score = Math.min(...Object.values(scores));
  
  if (isFinite(max_score)) {
    new_nodes = [];
    for (node of iter_nodes()) {
      if (node.id in scores) {
        nodescore = scores[node.id];
        newsize = scaleBetween(nodescore, min_size, max_size, min_score, max_score);
        // console.log(node.size, newsize);
        // node.size=newsize;
        node_d = nodes.get(node.id);
        node_d['size'] = newsize;
        // console.log(node_d);
        nodes.update(node_d);
      }
    }
    // nodes.update(new_nodes);
  } 

}


// function style_edges() {
//   for (edge of edges)
// }




function toggle_darkmode() {
  if (DARKMODE==1) { set_light_mode(); } else { set_dark_mode(); }
}

function set_dark_mode() {
  DARKMODE = 1;
  $('body').css('background-color', darkbgcolor);
  $('body').css('color', darktxtcolor);
  $('#tweet').css('background-color', darktweetbg);
  $('#tweet').css('border', '1px solid black');
  $('input').css('background-color', darkbgcolor);
  $('input').css('color', darktxtcolor);
  $('#nightmode').attr('src',darkimg);
  change_node_color(darktxtcolor);
  socket.emit('set_darkmode', DARKMODE);
}

function set_light_mode() {
DARKMODE = 0;

$('body').css('background-color', lightbgcolor);
$('body').css('color', lighttxtcolor);
$('#tweet').css('background-color', lighttweetbg);
$('#tweet').css('border', '1px solid lightgray');
$('input').css('background-color', lightbgcolor);
$('input').css('color', lighttxtcolor);
$('#nightmode').attr('src',lightimg);
change_node_color(lighttxtcolor);
socket.emit('set_darkmode', DARKMODE);
}

// var currentMousePos = { x: -1, y: -1 };
// $(document).mousemove(function(event) {
//   currentMousePos.x = event.pageX;
//   currentMousePos.y = event.pageY;
//   // console.log(currentMousePos.x, currentMousePos.y);
// });

// NETWORK EVENTS

network.on("hoverNode", function (params) {
  show_status_div(params);
});



network.on("click", function (_params) {
  node_d = get_node(_params);
  if (node_d == undefined) {
    hide_status_div();
  } else {
    console.log(node_d.id, MODE);
    // show_status_div(_params);

    switch(MODE) {
      case 'getcontext': 
        // console.log('switch: getting context')
        add_context(node_d.id);
        // hide_status_div();
        break;

      case 'markread':
        // console.log('switch: marking read')
        del_nodes(node_d.id);
        // hide_status_div();
        break;

      // default:
        // show_status_div(_params);
    }

    // window.open(node_d.id, '_blank');
  }
});

network.on("doubleClick", function (params) {
  $('#tweet').hide();
  // console.log(params);
  node_d = get_node(params);
  if (node_d != undefined) {
    del_nodes(node_d.id);
    // add_context(node_d);
    // window.open(node_d.id, '_blank');
  } else {
    request_updates();
  }
});

network.on("oncontext", function (params) {
  $('#tweet').hide();
  params.event.preventDefault();
  node_d = get_node(params);
  if (node_d != undefined) {
    // del_nodes(node_d.id);
    // window.open(node_d.id, '_blank');
    add_context(node_d);
  }
});





// socket events

function request_updates() {
  logmsg('refreshing');
  socket.emit('get_updates')
}

socket.on('get_updates', function(data) { update_nodes(data); });

// start
$(document).ready(function(){  
  startnet();
  
  
  setInterval(function() { socket.emit('get_pushes'); }, 1 * 1000);
  setInterval(function() { request_updates(); }, 30 * 1000);
  // setInterval(function() { size_nodes(); }, 31 * 1000);


  if (DARKMODE == 1) { set_dark_mode(); } else { set_light_mode(); }

  
});


// Other events

function set_mode_markread() {
  if (MODE!='markread') {
    MODE = 'markread';
    $('body').css('cursor', 'crosshair');
  }
}
function set_mode_getcontext() {
  if (MODE!='getcontext') {
    MODE = 'getcontext';
    $('body').css('cursor', 'help');
  }
}
function set_mode_default() {
  if (MODE!='default') {
    MODE = 'default';
    $('body').css('cursor', 'default');
  }
}


$(document).on('keydown', function (event) {
  if (event.ctrlKey | event.metaKey) {
      set_mode_markread();
  } else if (event.altKey) {
    set_mode_getcontext();
  } else {
    set_mode_default()
  }   
});

$(document).on('keyup', function (event) {
  set_mode_default();
});



function get_edge_ids() { 
  data = [];
  for ( edge of iter_edges() ) { data.push(edge.id); }
  return data;
}