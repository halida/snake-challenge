$ = jQuery

$ () ->
  window.builder = new MapBuilder("#map_builder")

class MapBuilder
  constructor: (e,w,h) ->
    @e = e = $(e)
    @grid = e.find(".grid")

    @setup_form()

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
    {
      walls: @walls()
      width: @width
      height: @height
    }
  at: (x,y) ->
    @rows[y][x]
  load_data: () ->
    @data = $.parseJSON @e.find(".data").text()
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


