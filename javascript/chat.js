$(document).ready(function(){
	$("#msg").focus();
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	var channel = new goog.appengine.Channel(token);
	var socket = channel.open();
	socket.onopen = function(){
		console.debug('onopen');
		$("#send").removeAttr("disabled");
	};
	socket.onmessage = function(message_in){
	console.debug('message in');
		$("#chatlog").append("\n" + message_in.data);
		$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));
	};
	socket.onerror = function(){
		$("#chatlog").append("\n--ERROR-- error in socket\n");
	};
	socket.onclose = function(){
		$("#chatlog").append("\n--INFO-- socket closed\n--INFO-- reload page to connect\n");
	};

	$("#form1").submit(function(){
		var path = "/" + room;
		var message = $(this).serialize();
		$.ajax({
			type: "POST",
			url: path,
			data: message,
			success: console.debug('sent' + message)
		});
		$("#msg").attr('value','');
		$("#msg").focus();
		return false;
	});
});
