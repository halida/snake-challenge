if MozWebSocket?
  WS = MozWebSocket
else
  WS = WebSocket

# chats
chat_ws = []

append = (msg) ->
  return unless msg
  mark = msg.substring(0, msg.indexOf(' '))
  color = random_color('p' + mark)
  $("#msgs").prepend ('<span style="color: '+color+'">'+msg+"</span>")
  $("#msgs").prepend "<br/>"

window.chat_init = (server, name, room) ->
  chat_ws = new WS(server)

  chat_ws.onopen = ->
    chat_ws.send JSON.stringify(
      name: name
      room: room
    )

  chat_ws.onmessage = (e) ->
    append e.data

  chat_ws.onclose = ->
    append "closed"

  $("#send-msg").show()
  $("#msg").focus()

window.chat_send = ->
  msg = $("#msg").val()
  return unless msg
  chat_ws.send JSON.stringify(msg: msg)
  $("#msg").val ""
