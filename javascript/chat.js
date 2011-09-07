$(document).ready(function(){
	$("#msg").focus();
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	
	init_channel(new goog.appengine.Channel(request_token(room)).open());

	$("#form1").submit(function(){
		var path = "/chat/" + room;
		var message = $("#msg").attr('value');
		$.ajax({
			type: 'POST',
			url: path,
			data: 'json={"type": "chat" , "content": {"text": "' + message + '" } }'
		});
		$("#msg").attr('value','');
		$("#msg").focus();
		return false;
	});
});

function request_token(room) {
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
			};
			return data.content.token;
		}
	});
}

function init_channel(socket) {

	socket.onopen = function(){
		$("#send").removeAttr("disabled");
		$("#chatlog").append("\nConnection established.\n");
	};
	
	socket.onmessage = function(msg){
		msg = JSON.parse(msg);
		switch(msg.data.type) {
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
		};
	};
	
	socket.onerror = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("\nConnection error. Attempting to reconnect..\n");
		
		var socket = new goog.appengine.Channel(request_token(room)).open();
		init_channel(socket);
	};
	
	socket.onclose = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("\nConnection closed.\n");
		
	};
}
