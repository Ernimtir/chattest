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
	
	$("#send").click(function(){
		var path = "/" + room + "?msg=" + $("#msg").val();
		var xhr = new XMLHttpRequest();
		xhr.open('POST', path, true);
		xhr.send();
		$("#msg").attr('value','');
		$("#msg").focus();
	});
	
	$("#msg").keydown(function(event){
		if (event.keyCode == '13') {
			event.preventDefault();
			$("#send").click();
		}
	});
});
