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
    MapBuilder.prototype.walls = function() {
      var box, row, walls, _i, _j, _len, _len2, _ref;
      walls = [];
      _ref = this.rows;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        row = _ref[_i];
        for (_j = 0, _len2 = row.length; _j < _len2; _j++) {
          box = row[_j];
          if (box.is_wall()) {
            walls.push(box.position());
          }
        }
      }
      return walls;
    };
    MapBuilder.prototype.to_json = function() {
      return {
        walls: this.walls()
      };
    };
    MapBuilder.prototype.create_grid = function() {
      var box, boxes, div, i, j, row, _results;
      this.rows = [];
      i = 0;
      _results = [];
      while (i < this.height) {
        row = $("<div>");
        this.e.append(row);
        boxes = [];
        this.rows.push(boxes);
        j = 0;
        while (j < this.width) {
          div = $("<div class='box'>");
          row.append(div);
          box = new Box(div, j, i);
          boxes.push(box);
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
      this.x = x;
      this.y = y;
      this.box.bind("click", __bind(function() {
        return this.box.toggleClass("wall");
      }, this));
    }
    Box.prototype.position = function() {
      return [this.x, this.y];
    };
    Box.prototype.is_wall = function() {
      return this.box.hasClass("wall");
    };
    return Box;
  })();
}).call(this);
