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
		$("#chatlog").append("\n" + msg.data);
		$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	};
	socket.onerror = function(){
		$("#chatlog").append("\nConnection error. Attempting to reconnect..\n");
		var path = "/tokenrequest";
		$.ajax({
			type: "POST",
			url: path,
			data: room,
			success: function(data){
				var socket = new goog.appengine.Channel(data.content.token).open();
				init_channel(socket);
			}
		});
	};
	socket.onclose = function(){
		$("#chatlog").append("\nConnection closed.\n");
	};
}
