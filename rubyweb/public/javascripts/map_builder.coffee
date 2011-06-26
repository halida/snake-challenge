$ = jQuery

$ () ->
  window.builder = new MapBuilder("#builder",15,15)

class MapBuilder
  constructor: (e,w,h) ->
    @e = e = $(e)
    @width = w
    @height = h
    @create_grid()
  walls: () ->
    walls = []
    for row in @rows
      for box in row
        if box.is_wall()
          walls.push(box.position())
    walls
  to_json: () ->
    {walls: @walls()}
  create_grid: () ->
    @rows = []
    i = 0
    while(i < @height)
      row = $("<div>")
      @e.append(row)
      boxes = []
      @rows.push(boxes)
      j = 0
      while(j < @width)
        div = $("<div class='box'>")
        row.append(div)
        box = new Box(div,j,i)
        boxes.push(box)
        j += 1
      i += 1

class Box
  constructor: (box,x,y) ->
    @box = box
    @x = x
    @y = y
    @box.bind "click", () =>
      @box.toggleClass("wall")
  position: () ->
    [@x,@y]
  is_wall: () ->
    @box.hasClass("wall")


