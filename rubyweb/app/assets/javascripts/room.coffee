scale = 15
colors =
  wall: "#8c8c8c"
  python: [ [ "#a5c9e7", "#08467b", "#3e9be9" ], [ "#88db99", "#0e7483", "#85f56b" ], [ "#a5c9e7", "#0a4846", "#3ae712" ], [ "#88db99", "#f3f00a", "#0db02c" ] ]
  ruby: [ [ "#eb88a9", "#b30c43", "#f81919" ], [ "#f45e5e", "#83103e", "#e07711" ], [ "#eb88a9", "#8151a6", "#59edef" ], [ "#f45e5e", "#f8952a", "#ffea00" ] ]
  dead: [ "#8c8c8c", "#8c8c8c", "#8c8c8c" ]
  portal: ["#bb0000", "#bb0022", "#bb0044", "#bb0066", "#bb0088"]

ws = undefined
canvas = undefined
ctx = undefined
map = undefined

server = undefined
room = -1

score_board_html = ""

user_snake_id=[]
user_seq= -1

window.run_application = (s, r, nows=false) ->
  $('.right-block .title_bar').live "click", ()->
    next = $(this).next()
    if next.is(':hidden')
      next.slideDown()
    else
      next.slideUp()

  canvas = $("#room-canvas")
  ctx = canvas[0].getContext("2d")

  room = r
  server = s

  return if nows
  init_ws()

init_ws = ()->
  ws = new window.WS(server)
  ws.onmessage = (e)->
    data = $.parseJSON(e.data)
    record_data(data) if onrecord
    onmessage(data)

  ws.onerror = (error) ->
    console.log error

  ws.onclose = ->
    error "connection closed, refresh please.."

  ws.onopen = ->
    ws.send JSON.stringify(op: 'setroom', room: room)
    ws.send JSON.stringify(op: 'map', room: room)
    ws.send JSON.stringify(op: 'info', room: room)


onmessage = (data)->
  switch data.op
    when "info"
      update_info data
      check_ai_info(data)
    when "add"
      add_user_result(data)
    when  "map"
      setup_map(data)
      check_ai_map(data)
    when "turn", "sprint"
      undefined
    else
      error data.status if data.status
      console.log(data)


update_info = (info) ->
  if info.logs
    for log in info.logs
      console.log log

  update info

  if user_seq >= 0
    snake = info.snakes[user_seq]
    console.log snake
    if snake and snake.alive
      $("#user-control-panel").show()
    else
      user_seq = -1
      $("#user-control-panel").hide()

update = (info) ->
  $('#map_round').html info.round
  $("#map_status").html info.status

  ctx.fillStyle = '#ffffff'
  ctx.fillRect 0, 0, ctx.canvas.width, ctx.canvas.height
  draw_walls()


  score_board_html = ""
  snakes = (snake for snake in info.snakes)
  snakes.sort (a, b) -> b.body.length - a.body.length
  for snake in snakes
    draw_snake snake
  $("#score_board").html score_board_html

  if info.portals.length > 0
    for i in [0..info.portals.length-1]
      portal = info.portals[i]
      ctx.fillStyle = colors.portal[i%2]
      ctx.fillRect portal[0] * scale, portal[1] * scale, scale, scale

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


draw_snake = (snake) ->

  color_set = (if snake.alive then choose_snake_color(snake) else colors.dead)
  ctx.fillStyle = color_set[0]
  for body in snake.body
    ctx.fillRect body[0] * scale, body[1] * scale, scale, scale

  head = snake.body[0]
  ctx.fillStyle = color_set[1]
  ctx.fillRect head[0] * scale, head[1] * scale, scale, scale
  ctx.fillStyle = color_set[2]
  ctx.fillRect head[0] * scale + 4, head[1] * scale + 4, scale - 8, scale - 8
  score_board_html += "<li class=\"" + (if snake.alive then snake.type else "dead")+"\">"\
    + "<div class=\"head\" style=\"background: "+color_set[1]+"\">" \
    + "<div class=\"head-inner\" style=\"background: "+color_set[2]+"\"></div></div>" \
    + "<div class=\"name\">" + snake.name + "</div>" \
    + "<div class=\"step\"><font>" + snake.body.length + "</font></div></li>"


draw_egg = (egg) ->
  ctx.drawImage document.getElementById("icon_egg"), egg[0] * scale, egg[1] * scale


draw_gem = (gem) ->
  ctx.drawImage document.getElementById("icon_gem"), gem[0] * scale, gem[1] * scale

draw_walls = ->
  return unless map
  ctx.fillStyle = colors.wall
  for wall in map.walls
    ctx.fillRect wall[0] * scale, wall[1] * scale, scale, scale

setup_map = (data)->
  map = data

  $('#map_name').html map.name
  $('#map_author').html 'by ' + map.author

  canvas.attr('width', data.size[0]*scale)
  canvas.attr('height', data.size[1]*scale)
  draw_walls()

window.add_user = (name, type) ->
  ws.send JSON.stringify(
    op: "add"
    room: room
    name: name
    type: type
  )

window.sprint = ()->
  return false if user_seq < 0
  ws.send JSON.stringify(
    op: "sprint"
    id: user_snake_id
    snake_id: user_snake_id
    room: room
    round: -1
  )
  return true

window.turn = (direction) ->
  return false if user_seq < 0
  ws.send JSON.stringify(
    op: "turn"
    id: user_snake_id
    snake_id: user_snake_id
    room: room
    direction: direction
    round: -1
  )
  return true

add_user_result = (data)->
  unless data.seq
    console.log data
    error data.status
    return

  user_seq = data.seq
  user_snake_id = data.id
  $("#user-control-panel").show()

  $(document).keyup (e)->
    dir = -1
    if (e.keyCode == 38 or e.keyCode == 87) # up w
      dir = 1
    if (e.keyCode == 37 or e.keyCode == 65) # left a
      dir = 0
    if (e.keyCode == 40 or e.keyCode == 83) # down s
      dir = 3
    if (e.keyCode == 39 or e.keyCode == 68) # right d
      dir = 2

    return unless dir >= 0
    e.preventDefault() if turn(dir)

# -------------------------------------------------
# ai

ai = undefined

check_ai_info = (info) ->
  return unless user_seq >= 0
  return unless ai

  direction = ai.step info
  turn direction
  # console.log(direction)

check_ai_map = (map)->
  return unless user_seq >= 0
  return unless ai

  ai.onmap map

window.set_ai = (ainame) ->
  ai = simple_snake
  ai.init(user_seq)
  ai.setmap map


# -------------------------------------------------
# replay
onrecord = false
onreplay = false
record = []
replay_seq = 0

window.toggle_record = ()->
  onrecord = not onrecord
  if onrecord
    $('#record-button').addClass('on')
    record = []
    record.push(map) #save map
  else
    $('#record-button').removeClass('on')

window.toggle_replay = ()->
  return if record.length <= 0
  onreplay = not onreplay
  if onreplay
    toggle_record() if onrecord
    $('#replay-button').addClass('on')
    if ws
      ws.onclose = ()-> undefined
      ws.close()
    replay_seq = 0
    replay()
  else
    $('#replay-button').removeClass('on')
    init_ws(server, room) if ws

record_data = (data)->
  $('#record-count').html(record.length)
  record.push data

replay = ()->
  return unless record
  return unless onreplay
  $('#replay-count').html(replay_seq)

  onmessage record[replay_seq]
  replay_seq = (replay_seq + 1) % record.length
  setTimeout(replay, 300)

window.save_replay = ()->
  return unless record
  $.post('/replays', {replay: {json: JSON.stringify(record)}, authenticity_token: $('#new_replay input[name=authenticity_token]').attr('value')}, (data)->
        notice(data.status)
        )

window.load_replay = (id)->
  $.get('/replays/'+id, {json: true}, (data)->
        record = data
        $('#record-count').html(record.length)
        notice("replay loaded")
        )

# -------------------------------------------------
# set map
window.set_map = (id)->
  $.get('/maps/'+id, {json: true}, (data)->
        set_map_data(data)
        )

set_map_data = (data)->
  ws.send(JSON.stringify(op: 'setmap', data: data, room: room))
  ws.send(JSON.stringify(op: 'map', room: room))