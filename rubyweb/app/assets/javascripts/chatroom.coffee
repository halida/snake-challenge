# chats
chat_ws = []

msg = (m) ->
  $("#debug-msg").text m

append = (msg) ->
  $("#msgs").prepend msg
  $("#msgs").prepend "<br/>"

window.chat_init = (server, name, room) ->
  chat_ws = new WebSocket(server)

  chat_ws.onopen = ->
    chat_ws.send JSON.stringify(
      name: name
      room: room
    )

  chat_ws.onmessage = (e) ->
    append e.data

  chat_ws.onclose = ->
    append "closed"

  $("#send-msg").show 200
  $("#msg").focus()

window.chat_send = ->
  msg = $("#msg").val()
  return unless msg
  chat_ws.send JSON.stringify(msg: msg)
  $("#msg").val ""
