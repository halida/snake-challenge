# hi
$ = jQuery

$ () ->
  window.builder = new MapBuilder("#builder",15,15)

class MapBuilder
  constructor: (e,w,h) ->
    @e = e = $(e)
    @width = w
    @height = h
    @create_grid()
  create_grid: () ->
    i = 0
    while(i < @height)
      row = $("<div>")
      @e.append(row)
      j = 0
      while(j < @width)
        box = $("<div class='box'>")
        row.append(box)
        new Box(box,j,i)
        j += 1
      i += 1

class Box
  constructor: (box,x,y) ->
    @box = box
    @box.data("x",x)
    @box.data("y",y)
    @box.bind "click", () =>
      @box.toggleClass("wall")


