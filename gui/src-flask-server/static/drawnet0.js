


var nodes = null;
var edges = null;
var network = null;

var DIR = "img/refresh-cl/";
var LENGTH_MAIN = 150;
var LENGTH_SUB = 50;





// Called when the Visualization API is loaded.
function draw(nodes = [], edges = []) {
  

  // create a network
  var container = document.getElementById("postnetviz");
  var data = {
    nodes: nodes,
    edges: edges,
  };
  var options = {
    
    // PHYSICS OPTIONS
    physics:{
      enabled: true,
      hierarchicalRepulsion: {
        centralGravity: 0.25,
        springLength: 100,
        springConstant: 0.01,
        nodeDistance: 120,
        damping: 0.09,
        avoidOverlap: 1
      },
      maxVelocity: 10,
      minVelocity: 0.001,
      solver: 'hierarchicalRepulsion',
      stabilization: {
        enabled: true,
        iterations: 200,
        updateInterval: 100,
        onlyDynamicEdges: false,
        fit: true
      },
      timestep: 0.5,
      adaptiveTimestep: true,
      wind: { x: 0, y: 0 }
    },



    // EDGES OPTIONS
    edges:{
      arrows: {
        to: {
          enabled: true,
          scaleFactor: 1,
          type: "arrow"
        },
      },
      endPointOffset: {
        from: 0,
        to: 0
      },
      arrowStrikethrough: true,
      chosen: true,
      color: {
        color:'#848484',
        highlight:'#848484',
        hover: '#848484',
        inherit: 'from',
        opacity:1.0
      },
      dashes: false,
      hidden: false,
      hoverWidth: 1.5,
      label: undefined,
      labelHighlightBold: true,
      length: undefined,
      physics: true,
      scaling:{
        min: 1,
        max: 15,
        label: {
          enabled: true,
          min: 14,
          max: 30,
          maxVisible: 30,
          drawThreshold: 5
        },
        customScalingFunction: function (min,max,total,value) {
          if (max === min) {
            return 0.5;
          }
          else {
            var scale = 1 / (max - min);
            return Math.max(0,(value - min)*scale);
          }
        }
      },
      selectionWidth: 1,
      selfReferenceSize: 20,
      selfReference:{
          size: 20,
          angle: Math.PI / 4,
          renderBehindTheNode: true
      },
      shadow:{
        enabled: false,
        color: 'rgba(0,0,0,0.5)',
        size:10,
        x:5,
        y:5
      },
      smooth: {
        enabled: false,
        type: "dynamic",
        roundness: 0.1
      },
      title:undefined,
      value: undefined,
      width: 1,
      widthConstraint: false
    },
    
    // LAYOUT OPTIONS
    layout: {
      randomSeed: 0.69,
      improvedLayout:true,
      clusterThreshold: 150,
      hierarchical: {
        enabled:false,
        levelSeparation: 150,
        nodeSpacing: 100,
        treeSpacing: 200,
        blockShifting: true,
        edgeMinimization: true,
        parentCentralization: true,
        direction: 'LR',        // UD, DU, LR, RL
        sortMethod: 'hubsize',  // hubsize, directed
        shakeTowards: 'leaves'  // roots, leaves
      }
    }, 

    
    // INTERACTION
    interaction:{
      dragNodes:true,
      dragView: true,
      hideEdgesOnDrag: false,
      hideEdgesOnZoom: false,
      hideNodesOnDrag: false,
      hover: true,
      hoverConnectedEdges: true,
      keyboard: {
        enabled: false,
        speed: {x: 10, y: 10, zoom: 0.02},
        bindToWindow: true,
        autoFocus: true,
      },
      multiselect: false,
      navigationButtons: false,
      selectable: true,
      selectConnectedEdges: true,
      tooltipDelay: 300,
      zoomSpeed: .1,
      zoomView: true,
    },


    // manipulation: {
    //   enabled: true,
    // },
  };





  network = new vis.Network(
    container,
    data, 
    options
  );

  network.on("hoverNode", function (params) {
    // console.log("hoverNode Event:", params);
    node = params.node;
    node_d = nodes[node-1];
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
      delnodes(nlx);
    }
  });
}












function popupwindow(url, title, w, h) {
  var left = (screen.width/2)-(w/2);
  var top = (screen.height/2)-(h/2);
  return window.open(url, title, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width='+w+', height='+h+', top='+top+', left='+left);
}



