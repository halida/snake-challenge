Chat = new Object;

Chat.add_message = function(name, body){
  var item = '<li class="item">';
  item += '<span class="name">'+name+':</span>';
  item += '<span class="body">'+body+'</span>';
  item += '</li>';

  $("#chat .items").append(item);
}

function send_message(){
  var message = $("#chat textarea").val();
  $("#chat textarea").val('');
  $.post("/chat/message", {message: message, channel: info.room_id});
}

$(document).ready(function(){
  var info = $.get("/chat/info");

  var chat = new Juggernaut;
  chat.subscribe(info.room_id, function(data){
    Chat.add_message(info.username, data);
  });

  $("#chat .new input")
  .click(function(e){
    send_message();
  })
  .keydown(function(e){
    if (e.ctrlKey && e.which=="0x0d") {
      send_message();
    }
  });

});
