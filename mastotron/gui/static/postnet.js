// vars
var FIXED = {x:false,y:false}
var MODE = 'default';
var SCORE_TYPE = 'All';
var darkbgcolor = 'rgb(20,20,23)'; //#28282B';
var lightbgcolor = '#eeeeee';
var lighttweetbg = 'white';
var darktweetbg = 'rgba(30,30,33, 0.9)'; //#28282B';
var darktxtcolor = 'white';
var lighttxtcolor = 'black';
var darkimg = "/static/dark-mode-6682-inv.png";
var lightimg = "/static/dark-mode-6682.png";
// var limnodesgraph = 15;
var limstack = 60;
var DARKMODE = get_dark_mode();
if (DARKMODE==1) { 
  var txtcolor = darktxtcolor; 
} else { 
  var txtcolor = lighttxtcolor;  
}
var nodebordercolor = '#6F0C80';
var DATA_STACK = [];


// start containers
var container = document.getElementById("postnetviz");
var nodes = new vis.DataSet();
var edges = new vis.DataSet();
var data = { nodes: nodes, edges: edges};
var options = {
  interaction:{
    hover: true,
    zoomView: false,
    zoomSpeed: .1,
    multiselect: true
  },

  edges:{
    color: "gray",
    arrows: {
      to: {
        enabled: true,
        scaleFactor: 1,
      },
      middle: { enabled: false },
      from: { 
        enabled: false,
        scaleFactor: .4,
      }
    },
    smooth: {
      enabled: true,
      type: "dynamic",
      roundness: 1
    },
  },

  nodes: {
    borderWidth: 0,
    size: 20,
    color: {
      // border: "#222222",
      // background: "#666666",
      // hover: "#777777"
    },
    font: { 
      color: txtcolor
    },
  },

  layout: {
    randomSeed: 69,
    improvedLayout:true,
    clusterThreshold: 150,
    hierarchical: {
      enabled:false,
      levelSeparation: 150,
      nodeSpacing: 25,
      treeSpacing: 50,
      blockShifting: true,
      edgeMinimization: true,
      parentCentralization: true,
      direction: 'UD',        // UD, DU, LR, RL
      sortMethod: 'directed',  // hubsize, directed
      shakeTowards: 'roots'  // roots, leaves
    }
  },

  physics:{
    enabled: true,
    forceAtlas2Based: {
      theta: 0.5,
      gravitationalConstant: 0,
      centralGravity: 0.0002,
      springConstant: 0.1,
      springLength: 1000,
      damping: 1,
      avoidOverlap: 1
    },
    hierarchicalRepulsion: {
      centralGravity: 0,
      springLength: 150,
      springConstant: 150,
      nodeDistance: 150,
      damping: 1,
      avoidOverlap: 1
    },
    barnesHut: {
      theta: 0.5,
      gravitationalConstant: 0.00001,
      centralGravity: 0.3,
      springLength: 95,
      springConstant: 0.0,
      damping: 0.09,
      avoidOverlap: 1
    },
    repulsion: {
      centralGravity: 0.05,
      springLength: 200,
      springConstant: 0.00005,
      nodeDistance: 100,
      damping: 1
    },    
    maxVelocity: 1,
    minVelocity: 1,
    solver: 'repulsion',
    stabilization: {
      enabled: true,
      iterations: 2000,
      updateInterval: .1,
      onlyDynamicEdges: false,
      fit: true
    },
    timestep: 1,
    adaptiveTimestep: true,
    // wind: { x: 0, y: -100 }
  },
  
};

var network = new vis.Network(container, data, options);

// FUNCTIONS

function startnet() {
  console.log('starting network!');
  socket.emit('start_updates');
  request_updates(lim=get_lim_nodes_graph());
}

function iter_edges() { return Object.values(network.body.edges); }
function iter_nodes() { return Object.values(network.body.nodes); }

function iter_nodes_d() { 
  newnodes=[];
  for (node of iter_nodes()) {
    node_d = nodes.get(node.id);
    if (node_d != null) {
      newnodes.push(node_d);
    }
  }
  return newnodes;
}


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
  _offset = 10;
  $('#tweet').html(node_d['html']);  
  x = node_pos_web['x'];
  y = node_pos_web['y'];
  $('#tweet').offset(
    { 
      top: y + _offset, 
      left: x + _offset
      // top:_offset,
      // right:0
    });
  $('#tweet').show();
}

function hide_status_div() { $('#tweet').fadeOut(500); }


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

function del_node(node_id, recursive = true) {
  if (recursive) {
    node_ids_to_del = getdownstreamnodes(node_id);
  } else {
    node_ids_to_del = [node_id];
  }

  del_nodes(node_ids_to_del);
  // style_nodes();
  get_more_nodes();
  // request_updates();
  // logmsg('marked '+node_id+' as read');
}

function del_nodes(node_ids) {
  hide_status_div();

  if (node_ids.length>0) {
    socket.emit('mark_as_read',node_ids);
    nodes.remove(node_ids);
    // style_nodes();
  }
}

function clear_network() {
  
  iter_nodes_d().forEach(function(node_d) {
    edgel=[];
    network.getConnectedEdges(node_d.id).forEach(function(edge_id) {
        edgel.push(edges.get(edge_id));
    });
    DATA_STACK.unshift({'nodes':[node_d], 'edges':edgel});
  });
  ids = get_all('id');
  nodes.remove(ids);
}

function add_context(node_id) {
  console.log('getting context for:',node_id);
  socket.emit('add_context', node_id)
}
function add_full_context(node_id) {
  console.log('getting full context for:',node_id);
  socket.emit('add_full_context', node_id)
}



// socket events


function lim_nodes_by_time() {
  times = [];
  todel = [];
  nodes.forEach(function(n) { times.push(n.timestamp)});
  nodes.forEach(function(n) { 
    rank = getIndexToIns(times, n.timestamp);
    if (rank > get_lim_nodes_graph()) {
      todel.push(n.id);
    }
  });
  nodes.remove(todel);
}

function lim_nodes(lim=0) {
  if(lim==0){lim=get_lim_nodes_graph();}
  if (nodes.length > lim) {
    console.log('<< lim_nodes',lim,'num nodes',nodes.length);

    todel=[];
    // toadd=[];
    iter_nodes_d().slice(0,nodes.length - lim).forEach(
      function(n){ todel.push(n.id); }
    );
    nodes.remove(todel);
    console.log('>> lim_nodes',lim,'num nodes',nodes.length);
  }
}

function update_nodes(data) {
  // freeze_nodes();
  nodes.update(data.nodes);
  edges.update(data.edges);
  reinforce_darkmode();
  style_nodes();
  // unfreeze_nodes();
  style_edges();
  // lim_nodes();
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function check_space_ready() {
  if (get_num_nodes() < get_lim_nodes_graph()) {
    get_more_nodes();
  }
}

function fix_nodes() {
  // return;
  // console.log('fix_nodes')
  iter_nodes().forEach(function(n){
    nd=nodes.get(n.id);
    if(nd) {
      nd.x=n.x;
      nd.y=n.y;
      nd.fixed=FIXED;
      // nodes.update(nd);
    }
  });
}

function freeze_nodes() {
  iter_nodes().forEach(function(n){
    nd=nodes.get(n.id);
    nd['x']=n.x;
    nd['y']=n.y;
    nd['fixed']={x:true,y:true}
    nodes.update(nd);
  });
}
function unfreeze_nodes() {
  nodes.forEach(function(nd){
    nd['fixed']=FIXED;
    nodes.update(nd);
  })
}


function style_edges() {
  for (edge of iter_edges()) {
    edge_d = edges.get(edge.id);
    if (edge_d.edge_type=='posted') {
      edge.options.arrows.to.type = 'circle';
      edge.options.arrows.from.type = 'circle';
      edge.options.arrows.to.enabled = false;
      edge.options.arrows.from.enabled = false;
    } else {
      edge.options.arrows.to.type = 'arrow';
      edge.options.arrows.from.type = 'bar';
      edge.options.arrows.to.enabled = true;
      edge.options.arrows.from.enabled = false;
    }
  }
}

function style_nodes() {
  repos_nodes();
  size_nodes();
  // nodes.forEach(function(n) { n.fixed={x: true, y: true} });
  for (node_d of iter_nodes_d()) {
    nedges = network.getConnectedEdges(node_d.id);
    if (node_d.num_replies>nedges.length) {
      node_d.color = nodebordercolor;
      node_d.borderWidth=5;
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

function get_num_nodes() { return nodes.length; }

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
      // score = node_d.timestamp;
      if (log) { score = Math.log10(score); }
      scores[node.id] = score;
    }
  }
  return scores;
}

function get_all_timestamps() {
  l=[];
  for (node_d of iter_nodes_d()) { l.push(node_d.timestamp); }
  return l;
}

function get_all(feat) {
  l=[];
  for (node_d of iter_nodes_d()) { l.push(node_d[feat]); }
  return l;
}


function rankBetween(unscaledNum, allUnscaledNums, minScale, maxScale) {
  rank = getIndexToIns(allUnscaledNums, unscaledNum + (Math.random()*.0001));
  return scaleBetween(
    rank,
    minScale,
    maxScale,
    0,
    allUnscaledNums.length,
  )
}

function scaleBetween(unscaledNum, minAllowed, maxAllowed, min, max) {
  return (maxAllowed - minAllowed) * (unscaledNum - min) / (max - min) + minAllowed;
}

function size_nodes(max_size=40, min_size=20, score_type=SCORE_TYPE, size_by='num_replies') {
  vals = get_all(size_by);
  nodes.forEach(function(nd) {
    newsizeby = nd[size_by] - network.getConnectedNodes().length;
    nd.size = rankBetween(newsizeby, vals, min_size, max_size);
    // nodes.update(nd);
  })
}

function size_nodes_score(max_size=40, min_size=20, score_type=SCORE_TYPE) {  
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
function reinforce_darkmode() {
  if (DARKMODE==1) { set_dark_mode(); } else { set_light_mode(); }
}

function set_dark_mode() {
  DARKMODE = 1;
  $('body').css('background-color', darkbgcolor);
  $('body').css('color', darktxtcolor);
  $('#tweet').css('background-color', darktweetbg);
  $('#pb-container').css('background-color', darktweetbg);
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

let OK_TO_DEL_ON_BLUR = false;

network.on("hoverNode", function (params) {
  node_d = get_node(params);
  network.selectNodes([node_d.id]); 
  show_status_div(params);
  setTimeout(function(){show_status_div(params);}, 1);
  setTimeout(function(){show_status_div(params);}, 5);
});

network.on("blurNode", function (params) {
  // network.unselectAll();
  // hide_status_div();
});

// network.on("stabilized", function(obj) {
//   logmsg('done stabilizing network');
//   console.log('stabilized',obj);
//   freeze_nodes();
// });



network.on("click", function (_params) {
  node_d = get_node(_params);
  console.log('clicked', _params.pointer.canvas);
  if (node_d == undefined) {
    hide_status_div();
  } else {
    // console.log('clicked:', node_d.id, node_d.is_read);
    node_id = node_d.id;
    e = _params.event.srcEvent;
    // if (e.ctrlKey | e.metaKey) {
    if (MODE=='markread') {
      // console.log('del node!',node_id);
      del_node(node_id);
    } else if (MODE=='getcontext') {
      add_context(node_id);
    }
    _params.event.def
  }
});

network.on("doubleClick", function (params) {
  // console.log('double clicked');
  node_d = get_node(params);
  if (node_d != undefined) {
    window.open(node_d.url_local, '_blank');
  } else {
    request_updates();
  }
});

network.on("oncontext", function (params) {
  $('#tweet').hide();
  params.event.preventDefault();
  node_d = get_node(params);
  if (node_d != undefined) {
    // del_node(node_d.id);
    // window.open(node_d.id, '_blank');
    add_context(node_d.id);
  }
});





// socket events

function get_our_status_for_updates(lim=1,force_push=false) {
  return {
    'ids_now':get_ids_in_graph_or_stack(), 
    'force_push':force_push, 
    'lim':lim
  };
}

function request_updates(lim=1, force_push=false) {
  ns=DATA_STACK.length.toString();
  if (DATA_STACK.length<=get_lim_nodes_stack()) {
    logmsg('refreshing with '+ns+' posts in queue @ '+get_time_str());
    socket.emit(
      'get_updates', 
      get_our_status_for_updates(
        lim=lim,
        force_push=force_push,
      )
    )
  } else {
    logmsg('idling with '+ns+' posts in queue @ '+get_time_str());
    // turnover_nodes();
  }
  get_more_nodes();
}

function turnover_nodes() {
  update_nodes(DATA_STACK.pop());
  lim_nodes();
}

function request_pushes() {
  // logmsg('checking pushes @ '+get_time_str());
  socket.emit('get_pushes', get_our_status_for_updates())
}

function get_ids_in_graph_or_stack() {
  ids = get_all('id');
  DATA_STACK.forEach(function(d) {
    d.nodes.forEach(function(n) {
      ids.push(n.id);
    });
  });
  return ids;
}

function receive_updates_with_stack(data) {
  if (data.force_push) {
    update_nodes(data);
    lim_nodes(lim=get_lim_nodes_graph());
  } else {
    maybe_add_to_stack(data);
  }
  get_more_nodes();
}


function receive_updates_with_stack_pushed(data) {
  update_nodes(data);
  lim_nodes();
}

socket.on('get_updates', function(data) {
  // console.log('got updates:',data);
  receive_updates_with_stack(data);
  // receive_updates_with_stack_pushed(data);
});

function maybe_add_to_stack(data) {
  // if(data.logmsg){logmsg('received '+data.logmsg + '; ' + DATA_STACK.length.toString() + ' in queue');}
  nn=data.nodes.length;
  logmsg('received '+nn+' posts with '+ns+' in queue @ '+get_time_str());
  DATA_STACK.push(data);
}

function get_more_nodes() {
  while ((DATA_STACK.length > 0) && (nodes.length < get_lim_nodes_graph())) {
    data = DATA_STACK.pop()
    if(data) {
      update_nodes(data);
    }
  }
}

socket.on('logmsg', function(msg) {if(msg){logmsg(msg)};});


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

function toggle_mode_read() {
  if (MODE=='markread') {
    set_mode_default();
  } else {
    set_mode_markread();
  }
}
function toggle_mode_info() {
  if (MODE=='getcontext') {
    set_mode_default();
  } else {
    set_mode_getcontext();
  }
}


$(document).on('keydown', function (event) {
  // console.log('event.which =',event.which);
  if (event.which==27) {   // escape
    set_mode_default();
    network.unselectAll();
    hide_status_div();
  } else if (event.ctrlKey | event.metaKey) {
    // console.log(event);
    if (event.which == 65) { // a (select all)
      event.preventDefault();
      node_ids = [];
      iter_nodes_d().forEach(function(nd){node_ids.push(nd.id)});
      network.selectNodes(node_ids);
    } 
    else if (event.which == 82) {
      // command r
      event.preventDefault();
      clear_network();
      get_more_nodes();
      request_updates(lim=get_lim_nodes_graph());
    }

    // } else {
      // r (refresh)
      // set_mode_markread();
      // toggle_mode_read();
    // }
  } else if (event.altKey) {
    // toggle_mode_info();
    // set_mode_getcontext();
  } else if ((event.which==88) | (event.which==82) | (event.which==8) | (event.which==46)) { // x or r or backspace or del
    // del_nodes(network.getSelectedNodes());
    network.getSelectedNodes().forEach(function(n){
      // console.log(n);
      del_node(n);
    })
  } else if (event.which==78) {  // n
    // request_updates();
    request_updates(lim=get_lim_nodes_graph(), force_push=true);
    // get_more_nodes();
  }
  // else {
    // set_mode_default()
  // }   
});

// $(document).on('keyup', function (event) {
//   set_mode_default();
// });



function get_edge_ids() { 
  data = [];
  for ( edge of iter_edges() ) { data.push(edge.id); }
  return data;
}

function repos_nodes(overwrite_x=false, overwrite_y=false) {
  var times = get_all('timestamp');
  var times_inv = []; times.forEach(function(x){times_inv.push(-1*x);});
  var scores = get_all('score');
  var scoresX = []; scores.forEach(function(x){scoresX.push(Math.random());});
  var canvas = document.getElementById('postnetviz');
  var width = canvas.scrollWidth;
  var height = canvas.scrollHeight;
  var max_w = (width/2) - 50;
  var max_h = (height/2) - 50;
  console.log(width,height, max_w,max_h);
  nodes.forEach(function(nd) {
    if(nd.x==nd.x) { nd.x=smudge(rankBetween(nd.score, scores, -1*max_w, max_w), fac=0); }
    if(nd.y==nd.y) { nd.y=smudge(rankBetween(-1*nd.timestamp, times_inv, -1*max_h, max_h), fac=0) - 50; }
    nodes.update(nd);
    // moveNodeAnim(nd.id, xx, yy, 1);
  });


    // y


    // if (overwrite_x | (nd.x==undefined)) {
    //   // nd.x = rankBetween(nd.timestamp, times, width/2,-1*width/2);
    //   new_x = rankBetween(-1*nd.timestamp, times_inv, width/2,-1*width/2);
    // } else {
    //   new_x = 
    // }
    // if (overwrite_y | (nd.y==undefined)) {
    //   // nd.y = rankBetween(nd.score, scores, height/2, -1*height/2);
      
    // }
    
};


// start
$(document).ready(function(){  
  startnet();

  // setInterval(function() { fix_nodes(); }, 1);  
  // setInterval(function() { get_more_nodes(); }, 500);
  setInterval(function() { request_pushes(); }, 500);
  setInterval(function() { request_updates(); },500);
  
  reinforce_darkmode();

  window.onresize = function() {network.fit();}
});

