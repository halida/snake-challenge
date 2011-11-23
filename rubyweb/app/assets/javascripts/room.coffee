walls = []
scale = 15
colors =
  wall: "#8c8c8c"
  python: [ [ "#a5c9e7", "#08467b", "#3e9be9" ], [ "#88db99", "#0e7483", "#85f56b" ], [ "#a5c9e7", "#0a4846", "#3ae712" ], [ "#88db99", "#f3f00a", "#0db02c" ] ]
  ruby: [ [ "#eb88a9", "#b30c43", "#f81919" ], [ "#f45e5e", "#83103e", "#e07711" ], [ "#eb88a9", "#8151a6", "#59edef" ], [ "#f45e5e", "#f8952a", "#ffea00" ] ]
  dead: [ "#8c8c8c", "#8c8c8c", "#8c8c8c" ]

ws = undefined

score_board_html = ""
finished = false
canvas = undefined
ctx = undefined
room = -1

user_snake_id=[]
user_seq= -1

window.run_application = (server, r) ->
  room = r
  canvas = $("#canvas")[0]
  ctx = canvas.getContext("2d")

  ws = new WebSocket(server)
  ws.onmessage = (e) ->
    data = $.parseJSON(e.data)

    switch data.op
      when "info"
        update_room data
      when "add" #add user success
        user_seq = data.seq
        user_snake_id = data.id
        $("#user-control-panel").show()

  ws.onerror = (error) ->
    console.log error

  ws.onclose = ->
    alert "connection closed, refresh please.."

  ws.onopen = ->
    ws.send "room:" + room


update_room = (info) ->
  if walls.length <= 0
    setup_walls_data()

  if finished
    unless info.status is "finished"
      setup_walls_data()
      finished = false
  else
    update info
    finished = info.status is "finished"


update = (info) ->
  canvas.width = canvas.width
  score_board_html = ""
  draw_walls()
  $("#round_counter").html info.round + " " + info.status
  $.each info.snakes.sort((a, b) ->
    b.body.length - a.body.length
  ), (index) ->
    draw_snake this, index % 4

  $("#score_board").html score_board_html
  $.each info.eggs, ->
    draw_egg this

  $.each info.gems, ->
    draw_gem this

choose_snake_color = (snake)->
  v = 0
  for k in snake.name
    v += k.charCodeAt()
    v *= 13
    v %= 13626
  colors[snake.type][v % colors[snake.type].length]

draw_snake = (snake, color_index) ->
  color_set = (if snake.alive then choose_snake_color(snake) else colors.dead)
  ctx.fillStyle = color_set[0]
  $.each snake.body, ->
    ctx.fillRect this[0] * scale, this[1] * scale, scale, scale

  head = snake.body[0]
  ctx.fillStyle = color_set[1]
  ctx.fillRect head[0] * scale, head[1] * scale, scale, scale
  ctx.fillStyle = color_set[2]
  ctx.fillRect head[0] * scale + 4, head[1] * scale + 4, scale - 8, scale - 8
  score_board_html += "<li class=\"" + (if snake.alive then snake.type else "grey") + "\"><img src=\"/assets/icons/" + snake.type + color_index + ".gif\" /><h2>" + snake.name + "</h2><div class=\"step\"><font>" + snake.body.length + "</font></div></li>"

draw_egg = (egg) ->
  ctx.drawImage document.getElementById("icon_egg"), egg[0] * scale, egg[1] * scale

draw_gem = (gem) ->
  ctx.drawImage document.getElementById("icon_gem"), gem[0] * scale, gem[1] * scale

draw_walls = ->
  ctx.fillStyle = colors.wall
  $.each walls, ->
    ctx.fillRect this[0] * scale, this[1] * scale, scale, scale

setup_walls_data = ->
  $.getJSON "map", (map) ->
    walls = map.walls

window.add_user = (name, type) ->
  ws.send JSON.stringify(
    op: "add"
    room: room
    name: name
    type: type
  )

window.turn = (direction) ->
  return if user_seq < 0
  ws.send JSON.stringify(
    op: "turn"
    id: user_snake_id
    snake_id: user_snake_id
    room: room
    direction: direction
    round: -1
  )

