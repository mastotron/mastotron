function login() {
acct_name = $('#configform_account').val();
code = $('#configform_code').val();
if (acct_name && code) {
    $('#configform_code_div').hide();
    $('#configform_code').val('');
    socket.emit('do_login', {account:acct_name, code:code})
} else if (acct_name) {
    socket.emit('set_acct_name', {account:acct_name})
    console.log('setting account name');
}
}




$( "#configform" ).submit(function( e ) {
e.preventDefault();
login();
});

$( "#configform" ).on('keypress',function(e) {
if(e.which == 13) {
    login();
}
});


socket.on('get_auth_url', function(e){
$('#configform_code_div').show();
$('#configform_code').focus();
url = e.url;
popupwindow(url, 'Authenticate Mastodon', 500, 700);
});

socket.on('logged_in', function(e){
console.log(e);
// $('#configform_code_div').show();
});




$(document).ready(function(){ login(); })