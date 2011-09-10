$(document).ready(function(){
	$("#msg").focus();
	var socket = create_channel(room);
	var msgobj;
	$("#form1").submit(function(){
	msgobj.type = "chat";
	msgobj.content = {};
	msgobj.content.message = $("#msg").attr('value');
		var path = "/chat/" + room;
		var message = 'json='+JSON.stringify(msgobj);
		$.ajax({
			type: 'POST',
			url: path,
			data: msgdata
		});
		$("#msg").attr('value','');
		$("#msg").focus();
		return false;
	});
});

$(window).load(function() {
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
});

function create_channel(room) {
	var msgobj = {};
	msgobj.type = "system";
	msgobj.content = {};
	msgobj.content.room = room;
	var path = "/tokenrequest";
	var message = 'json='+JSON.stringify(msgobj);
	$.ajax({
		type: "POST",
		url: path,
		data: message,
		success: function(data){
			var dataJSON = JSON.parse(data);
			if(dataJSON.type == "connect"){
				var token = dataJSON.content.token;
				$("#chatlog").append("<br />Recieved token.");
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
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
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	socket.onopen = function(){
		$("#send").removeAttr("disabled");
		$("#chatlog").append("<br />Connection established.");
		$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	};
	
	socket.onmessage = function(msg){
		msgobj = JSON.parse(msg.data);
		switch(msgobj.type) {
			case "chat":
				$("#chatlog").append("<br />" + msgobj.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "alert":
				$("#chatlog").append("<br />" + msgobj.content.text);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
			case "connect":
				//nothing yet
				break;
			case "disconnect":
				//nothing yet
				break;
			default:
				$("#chatlog").append("<br />Bad Message Recieved: " + msgobj.data);
				$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
				break;
		};
	};
	
	socket.onerror = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("<br />Connection error. Attempting to reconnect..<br />");
		$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
		
		create_channel(room);
	};
	
	socket.onclose = function(){
		$("#send").attr("disabled", "disabled");
		$("#chatlog").append("<br />Connection closed.<br />");
		$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
		
	};
}
