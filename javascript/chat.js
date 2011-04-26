$(document).ready(function(){
	$("#msg").focus();
	$("#chatlog").scrollTop(parseInt($("#chatlog")[0].scrollHeight));

	var socket = new goog.appengine.Channel(token).open();
	socket.onopen = function(){
		$("#send").removeAttr("disabled");
	};
	socket.onmessage = function(msg){
		$("#chatlog").append("\n" + msg.data);
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
		alert("sending " + message);
		$.ajax({
			type: "POST",
			url: path,
			data: message,
			success: function() {
				alert("sent "+ message);
			}

		});
		$("#msg").attr('value','');
		$("#msg").focus();
		return false;
	});
});
