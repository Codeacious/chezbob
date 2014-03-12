
var rpc = new $.JsonRpcClient({ajaxUrl: '/api'});

function notify_error(error)
{
	alert(error);
}

function handle_login()
{
	//capture username and password
	var username = $("#login-username").text();
	var password = $("#login-password").text();
	
	//silly crypt will require that we get the crypted password first for a salt.
	var salt = ""
	rpc.call('Bob.getcrypt', [username], function (result) {
		alert(result);
		var cryptedPassword = unixCryptTD(password, result)
		alert(cryptedPassword);
	},
	function (error)
	{
		notify_error(error);
	}
	);
}

$(document).ready(function() {
	$("#btn-login").on("click", handle_login);
});