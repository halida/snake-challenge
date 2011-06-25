(function() {
  var $, Box, MapBuilder;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  $ = jQuery;
  $(function() {
    return window.builder = new MapBuilder("#builder", 15, 15);
  });
  MapBuilder = (function() {
    function MapBuilder(e, w, h) {
      this.e = e = $(e);
      this.width = w;
      this.height = h;
      this.create_grid();
    }
    MapBuilder.prototype.create_grid = function() {
      var box, i, j, row, _results;
      i = 0;
      _results = [];
      while (i < this.height) {
        row = $("<div id='row_" + i + "'></div>");
        this.e.append(row);
        j = 0;
        while (j < this.width) {
          box = $("<div id='box_" + i + "_" + j + "' class='box'>");
          row.append(box);
          new Box(box, j, i);
          j += 1;
        }
        _results.push(i += 1);
      }
      return _results;
    };
    return MapBuilder;
  })();
  Box = (function() {
    function Box(box, x, y) {
      this.box = box;
      this.box.data("x", x);
      this.box.data("y", y);
      this.box.bind("click", __bind(function() {
        return this.box.toggleClass("wall");
      }, this));
    }
    return Box;
  })();
}).call(this);
