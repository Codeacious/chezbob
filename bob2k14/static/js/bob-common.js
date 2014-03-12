
var rpc = new $.JsonRpcClient({ajaxUrl: '/api'});

function notify_error(error)
{
	bootbox.alert("Error: " + error);
}

function handle_login()
{
	//capture username and password
	var username = $("#login-username").val();
	var password = $("#login-password").val();
	
	//silly crypt will require that we get the crypted password first for a salt.
	var salt = ""
	rpc.call('Bob.getcrypt', [username], function (result) {
		bootbox.alert(result);
		var cryptedPassword = unixCryptTD(password, result)
		bootbox.alert(cryptedPassword);
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