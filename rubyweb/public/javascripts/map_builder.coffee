$ = jQuery

json = (e) ->
  $.parseJSON $(e).text()

exists = (e) ->
  $(e).size() > 0

$ () ->
  window.builder = new MapBuilder("#map_builder") if exists("#map_builder")
  if exists("ul#maps")
    window.previews = $("ul#maps li").map (i,e) ->
      new MapPreview(e)
    window.pr = window.previews[0]

class Map
  constructor: (e) ->
    @e = $(e)
  at: (x,y) ->
    (row = @boxes[y]) && row[x]
  draw: (data) ->
    @draw_grid(data.width,data.height)
    @draw_walls(data.walls)
  draw_walls: (walls) ->
    for [x,y] in walls
      @at(x,y)?.be_wall()
  draw_grid: (w,h) ->
    @grid = $("<div class='grid'>")
    @boxes = for i in [0...h]
      row = $("<div class='row'>")
      @grid.append row
      for j in [0...w]
        div = $("<div class='box'>")
        row.append div
        new Box(div,i,j)
    @e.append @grid

class MapPreview
  constructor: (e) ->
    @e = $(e)
    @data = json @e.find(".data")
    @preview = @e.find(".preview")
    @map = new Map(@preview)
    @map.draw(@data)

class MapBuilder
  constructor: (e) ->
    @e = e = $(e)
    @grid = e.find(".grid")

    @setup_form()
    @_height = e.find("#map_height").change () =>
      @adjust_dimension()
    @_width = e.find("#map_width").change () =>
      @adjust_dimension()

    # load & draw map
    @load_data()
    @create_grid()
    @draw_walls()
  walls: () ->
    walls = []
    for row in @rows
      for box in row
        if box.is_wall()
          walls.push(box.position())
    walls
  to_json: () ->
    walls: @walls()
    width: @width
    height: @height

  redraw: () ->
    @grid.remove()
    @grid = $("<div class='grid'>")
    @e.prepend(@grid)
    @create_grid()
    @draw_walls()
  adjust_dimension: () ->
    @height = @_height.val()
    @width = @_width.val()
    @redraw()
  at: (x,y) ->
    @rows[y][x]
  load_data: () ->
    @data = json @e.find(".data")
    return unless @data
    @width = @data.width
    @height = @data.height
  draw_walls: () ->
    for [x,y] in @data.walls
      @at(x,y)?.be_wall()
  setup_form: () ->
    @form = @e.find("form")
    @form.find(":submit").click () =>
      @form.find("#map_builder_data").val(JSON.stringify @to_json())
  create_grid: () ->
    @rows = []
    i = 0
    while(i < @height)
      row = $("<div>")
      @grid.append(row)
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
      @be_wall()
  be_wall: () ->
    @box.toggleClass("wall")
  position: () ->
    [@x,@y]
  is_wall: () ->
    @box.hasClass("wall")


