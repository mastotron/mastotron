var ALREADY_UPDATED=false;

var PAUSE=false;
var TIME_TIL_UPDATE = 2.5;
var TIME_TIL_MOVED = 0.5;


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

msg=`
<p>Mastotron is a different, (for now read-only) interface to Mastodon. Simply connect your account via OAuth and interact with your timeline in a different way.</p>

<li>Hover over a node to read it.</li>
<li>Right-click it to load replies.</li>
<li>Press (D) to dismiss it.</li>
<li>Press (C) to load its context/replies into the network.</li>
<li>Press (R) to refresh data.</li>
<li>Press (L) for latest in queue.</li>
<li>Press (N) for next in queue.</li>

<p>Crucially, <i>a dismissed post will never re-appear.</i> This is good! It means you can "mark as read" a post and by never seeing it again you can trust that more of your timeline is new content.</p>

<p>This is the alpha, prebeta variant of this code so if it breaks try just closing the browser window and restarting the program.</p>
`

function gethelpmsg() {
  pb.alert(
    function() {},
    msg,
    'OK',                       // Ok text
    {closeWithEscape: true},
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
  // return socket.emit('set_config', CONFIG); 
}

function set_in_config(k,v) {
  CONFIG[k]=v;
  socket.emit('set_config', k, v);
}
function get_in_config(k,dflt=undefined) {
  v=CONFIG[k];
  if(v!=undefined){return v;} else { return dflt; }
}

function get_dark_mode() { return get_in_config('DARKMODE',0); }
var DARKMODE = get_dark_mode();

function set_dark_mode_opt(mode) { return set_in_config('DARKMODE',mode); }



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

function get_lim_nodes_stack() { 
  return get_lim_nodes_graph() * 2;
  // return get_in_config('LIM_NODES_STACK',60); 
}
function set_lim_nodes_stack(lim) { return set_in_config('LIM_NODES_STACK',lim); }






function toggle_darkmode() {
  if (DARKMODE==1) { set_light_mode(); } else { set_dark_mode(); }
}
function reinforce_darkmode() {
  if (DARKMODE==1) { set_dark_mode(); } else { set_light_mode(); }
}








function toggle_playpause() { console.log('????',PAUSE); set_playpause(!PAUSE); }

function set_playpause(pause) {
  PAUSE=pause;
  set_in_config('pause',PAUSE);
  if(PAUSE){
    $('#playpause').text('▶');
    $('#playpause').css('font-size','.7em');
    $('#playpause').attr('title','Allow new posts to cycle');
  } else {
    $('#playpause').text('■');
    $('#playpause').css('font-size','1em');
    $('#playpause').attr('title','Pass new posts to queue');
  }
}


function get_speed_update() {
  return get_in_config('TIME_TIL_UPDATE', TIME_TIL_UPDATE);
}
function set_speed_update(speed) {
  speed=Number(speed);
  if (!(isNaN(speed))) {
    if(speed>0.1) {
      set_in_config('TIME_TIL_UPDATE', speed)
      TIME_TIL_UPDATE = speed;
      set_intervals();
    }
  }
}

function get_speed_move() {
  return get_in_config('TIME_TIL_MOVED', TIME_TIL_MOVED);
}
function set_speed_move(speed) {
  speed=Number(speed);
  if (!(isNaN(speed))) {
    if(speed>0.1) {
      return set_in_config('TIME_TIL_MOVED', speed);
      TIME_TIL_MOVED=speed;
    }
  }
}

function prompt_for_speed() {
  pb.prompt(
      function(newnum) { set_speed_update(newnum); },
      'How many seconds between pulses?', // Message text
      'number',                       // Input type
      TIME_TIL_UPDATE,      // Default value
      'Set',                          // Submit text
      'Cancel',                       // Cancel text
      {showTimerBar: false}                              // Additional options
  );  
  reinforce_darkmode();
}


function stop_spinner() {
  $('#spinner').hide();
}

function set_spinner() {
  $('#spinner').show();
}



$(document).ready(function(){  
  reinforce_darkmode();
  set_playpause(get_in_config('pause'));
  if(!ALREADY_UPDATED){set_spinner();}
  // set_speed_update(get_in_config('TIME_TIL_UPDATE'));
});





