$(document).ready(function(){
	$("#msg").focus();
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));

	var socket = new goog.appengine.Channel(token).open();
	init_channel(socket)

	$("#form1").submit(function(){
		var path = "/" + room;
		var message = $(this).serialize();
		$.ajax({
			type: "POST",
			url: path,
			data: message
		});
		$("#msg").attr('value','');
		$("#msg").focus();
		return false;
	});
});

function init_channel(socket) {

	socket.onopen = function(){
		$("#send").removeAttr("disabled");
		$("#chatlog").append("\nConnection established.\n");
	};
	
	socket.onmessage = function(msg){
		switch(msg.data.type)
		{
			case "chat":
				$("#chatlog").append("\n" + msg.data.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "alert":
				$("#chatlog").append("\n" + msg.data.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "connect":
				//nothing yet
				break;
			case "disconnect":
				//nothing yet
				break;
			default:
				$("#chatlog").append("\nBad Message Recieved: " + msg.data);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
		}
	};
	
	socket.onerror = function(){
		$("#chatlog").append("\nConnection error. Attempting to reconnect..\n");
		var path = "/tokenrequest";
		$.ajax({
			type: "POST",
			url: path,
			data: room,
			success: function(data){
				if(data.type != "reconnect"){
					$("#chatlog").append("\nReconnection error. Please reload page.");
					$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
					return;
				}
				var socket = new goog.appengine.Channel(data.content.token).open();
				init_channel(socket);
			}
		});
	};
	
	socket.onclose = function(){
		$("#chatlog").append("\nConnection closed.\n");
	};
}
