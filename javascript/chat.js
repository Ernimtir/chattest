$(document).ready(function(){
	$("#msg").focus();
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	
	var socket = create_channel(room);
	
	

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

function create_channel(room) {
	var path = "/tokenrequest";
	var message = 'json={"type": "system", "content":{"room": "'+room+'"}}'
	$.ajax({
		type: "POST",
		url: path,
		data: message,
		success: function(data){
			var dataJSON = JSON.parse(data);
			if(dataJSON.type == "connect"){
				var token = dataJSON.content.token;
				$("#chatlog").append("<br />Recieved token.");
				var channel = new goog.appengine.Channel(token);
				var socket = channel.open();
				init_channel(socket);
				return socket;
			};
			$("#chatlog").append("<br />Connection error. Please reload page.");
			$("#chatlog").append("<br />"+data);
			$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
			return;
		}
	});
}

function init_channel(socket) {
	$("#chatlog").append("<br />Initializing...");
	socket.onopen = function(){
		$("#send").removeAttr("disabled");
		$("#chatlog").append("<br />Connection established.");
	};
	
	socket.onmessage = function(msg){
		msg = JSON.parse(msg);
		switch(msg.data.type) {
			case "chat":
				$("#chatlog").append("<br />" + msg.data.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "alert":
				$("#chatlog").append("<br />" + msg.data.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "connect":
				//nothing yet
				break;
			case "disconnect":
				//nothing yet
				break;
			default:
				$("#chatlog").append("<br />Bad Message Recieved: " + msg.data);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
		};
	};
	
	socket.onerror = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("<br />Connection error. Attempting to reconnect..<br />");
		
		create_channel(room);
	};
	
	socket.onclose = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("<br />Connection closed.<br />");
		
	};
}
