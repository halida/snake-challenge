Chat = new Object;

Chat.add_message = function(name, body){
  var item = '<li class="item">';
  item += '<span class="name">'+name+':</span>';
  item += '<span class="body">'+body+'</span>';
  item += '</li>';

  $("#chat .items").append(item);
}

function send_message(){
  var message = $("#chat input.message").val();
  $("#chat input.message").val('');
  $.post("/chat/message", {message: message, channel: Chat.info.room_id});
}

$(document).ready(function(){
  $.getJSON("/chat/info", function(info){
    Chat.info = info;

    var chat = new Juggernaut;
    chat.subscribe(info.room_id, function(data){
      Chat.add_message(info.username, data);
    });

    $("#chat .new input.message").keydown(function(e){
      if (e.ctrlKey && e.which=="0x0d") {
        send_message();
      }
    });

    $("#chat .new input[value='Send']").click(function(e){
      send_message();
    })
  });

});
