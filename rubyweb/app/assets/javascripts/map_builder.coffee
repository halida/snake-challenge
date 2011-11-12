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
    # remove old instance of the drawn grid if it exists
    grid = @e.find(".grid")
    grid.remove() if grid.size() > 0
    @draw_grid(data.width,data.height)
    @draw_walls(data.walls)
  draw_walls: (walls) ->
    for [x,y] in walls
      @at(x,y)?.be_wall()
  draw_grid: (w,h) ->
    @grid = $("<div class='grid'>")
    @boxes = for y in [0...h]
      row = $("<div class='row'>")
      @grid.append row
      for x in [0...w]
        div = $("<div class='box'>")
        row.append div
        new Box(div,x,y)
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

    @data = json @e.find(".data")
    @map = new Map(@e.find(".map"))
    @map.draw(@data)

  walls: () ->
    walls = []
    for row in @map.boxes
      for box in row
        if box.is_wall()
          walls.push(box.position())
    walls
  to_json: () ->
    walls: @walls()
    width: @_width.val()
    height: @_height.val()
  adjust_dimension: () ->
    @map.draw(@to_json())
  setup_form: () ->
    @form = @e.find("form")
    @form.find(":submit").click () =>
      @form.find("#map_builder_data").val(JSON.stringify @to_json())

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


