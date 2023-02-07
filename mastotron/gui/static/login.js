function prompt_for_username(username_now='') {  
    pb.prompt(
      function(val) { pb.clear(); login_user_name(val); },
      'Which mastodon account would you like to connect to mastotron? (username@server.com)', // Message text
      'text',                         // Input type
      username_now,                             // Default value
      'Login',                        // Submit text
      'Cancel',                       // Cancel text
      {}                              // Additional options
    );
    reinforce_darkmode();
  }
  
  function login_user_name(value) {
    if(value){
      console.log('setting account name');
      socket.emit('set_acct_name', {acct:value});
    }
  }
  
  function prompt_for_code(acct,url) {
    pb.prompt(
      function(code) { pb.clear(); login_with_code(acct,code) },
      'Please paste the activation code you received for the Mastodon account "'+acct+'" in the popup window. (Click <a href="'+url+'" target="_blank">here</a> if you can\'t find the popup window.)', // Message text
      'text',                         // Input type
      '',                             // Default value
      'Login',                        // Submit text
      'Cancel',                       // Cancel text
      {}                              // Additional options
    );
    reinforce_darkmode();
  }
  
  function login_with_code(acct,code) {
    console.log('setting code');
    socket.emit('do_login', {acct:acct, code:code})
  }
  




socket.on('get_auth_url', function(e){
    popupwindow(e.url, 'Authenticate Mastodon', 500, 700);
    prompt_for_code(e.acct, e.url);
});

socket.on('login_succeeded', function(e){
    setTimeout(
      function(){location.reload();},
      1000
    );
  
    pb.success(
      "Success: "+e.acct+" logged into mastotron",
      {
        duration:1000
      }
    );
});


socket.on('invalid_user_name', function(d) {
  pb.error('The account name entered ('+d.acct+') is invalid.', {duration:0});
  prompt_for_username(d.acct);
})

socket.on('server_not_giving_code', function(d) {
  pb.error('The server ('+d.server+') is not responding with an activation code. Are you sure "'+d.acct+'" is the correct account name?',{ duration:0 });
  prompt_for_username(d.acct);
})



