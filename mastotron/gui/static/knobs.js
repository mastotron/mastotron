var pb = new PromptBoxes({toasts: {duration: 2500, allowClose: true}});

function prompt_for_num_nodes() {
    pb.prompt(
        function(newnum) { set_lim_nodes_graph(newnum); },
        'How many posts can be shown on the screen at once?', // Message text
        'number',                         // Input type
        get_lim_nodes_graph(),                   // Default value
        'Set',                        // Submit text
        'Cancel',                       // Cancel text
        {showTimerBar: false}                              // Additional options
    );  
    reinforce_darkmode();
}

msg='<li>Double-clicking a node will bring you to it in a browser.</li>';
msg+='<li>Right-clicking it will bring its replies into the network.</li>'
msg+='<li>Double-clicking an empty spot or pressing 🇳 will force updates.</li>'
msg+='<li>For more posts to arrive, mark existing ones "read" by hovering over them and pressing 🇷.</li>'


function gethelpmsg() {
  pb.alert(
    function() {},
    msg,
    'OK',                       // Ok text
    {}                          // Additional options
  );
  $('#pb-container').css('max-width','700px');
  reinforce_darkmode();
}


function req_config() { 
  return socket.emit('req_config'); 
}
socket.on('res_config',function(d) {
  for (k of Object.keys(d)) {
    CONFIG[k]=d[k];
  }
});
function set_config() { 
  return socket.emit('set_config', CONFIG); 
}

function set_in_config(k,v) {
  CONFIG[k]=v;
  return set_config();
}
function get_in_config(k,dflt=undefined) {
  v=CONFIG[k];
  if(v!=undefined){return v;} else { return dflt; }
}

function get_dark_mode() { return get_in_config('DARKMODE',0); }
function set_dark_mode(mode) { return set_in_config('DARKMODE',mode); }

function get_lim_nodes_graph(dflt=15) { 
  res=get_in_config('LIM_NODES_GRAPH',dflt); 
  if(res){return res;}
  return dflt;
}
function set_lim_nodes_graph(lim) { 
  console.log(lim);
  num=Number(lim);
  if (!(isNaN(num))) {
    console.log('setting lim!',num);
    set_in_config('LIM_NODES_GRAPH',num); 
  }

  if(get_num_nodes() <= lim) { 
    get_more_nodes();
  } else {
    lim_nodes();
  }
}

function get_lim_nodes_stack() { return get_in_config('LIM_NODES_STACK',60); }
function set_lim_nodes_stack(lim) { return set_in_config('LIM_NODES_STACK',lim); }