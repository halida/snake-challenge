(function() {
  var $, Box, MapBuilder, MapPreview, exists, json;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  $ = jQuery;
  json = function(e) {
    return $.parseJSON($(e).text());
  };
  exists = function(e) {
    return $(e).size() > 0;
  };
  $(function() {
    if (exists("#map_builder")) {
      window.builder = new MapBuilder("#map_builder");
    }
    if (exists("ul#maps")) {
      window.previews = $("ul#maps li").map(function(i, e) {
        return new MapPreview(e);
      });
      return window.pr = window.previews[0];
    }
  });
  MapPreview = (function() {
    function MapPreview(e) {
      this.e = $(e);
      this.data = json(this.e.find(".data"));
      this.preview = this.e.find(".preview");
      this.draw_grid();
      this.draw_walls();
    }
    MapPreview.prototype.at = function(x, y) {
      var row;
      return (row = this.boxes[y]) && row[x];
    };
    MapPreview.prototype.draw_walls = function() {
      var x, y, _i, _len, _ref, _ref2, _ref3, _results;
      _ref = this.data.walls;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        _ref2 = _ref[_i], x = _ref2[0], y = _ref2[1];
        _results.push((_ref3 = this.at(x, y)) != null ? _ref3.be_wall() : void 0);
      }
      return _results;
    };
    MapPreview.prototype.draw_grid = function() {
      var div, h, i, j, row, w;
      h = this.data.height;
      w = this.data.width;
      this.grid = $("<div class='grid'>");
      this.boxes = (function() {
        var _results;
        _results = [];
        for (i = 0; 0 <= h ? i < h : i > h; 0 <= h ? i++ : i--) {
          row = $("<div class='row'>");
          this.grid.append(row);
          _results.push((function() {
            var _results2;
            _results2 = [];
            for (j = 0; 0 <= w ? j < w : j > w; 0 <= w ? j++ : j--) {
              div = $("<div class='box'>");
              row.append(div);
              _results2.push(new Box(div, i, j));
            }
            return _results2;
          })());
        }
        return _results;
      }).call(this);
      return this.preview.append(this.grid);
    };
    return MapPreview;
  })();
  MapBuilder = (function() {
    function MapBuilder(e) {
      this.e = e = $(e);
      this.grid = e.find(".grid");
      this.setup_form();
      this._height = e.find("#map_height").change(__bind(function() {
        return this.adjust_dimension();
      }, this));
      this._width = e.find("#map_width").change(__bind(function() {
        return this.adjust_dimension();
      }, this));
      this.load_data();
      this.create_grid();
      this.draw_walls();
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
        walls: this.walls(),
        width: this.width,
        height: this.height
      };
    };
    MapBuilder.prototype.redraw = function() {
      this.grid.remove();
      this.grid = $("<div class='grid'>");
      this.e.prepend(this.grid);
      this.create_grid();
      return this.draw_walls();
    };
    MapBuilder.prototype.adjust_dimension = function() {
      this.height = this._height.val();
      this.width = this._width.val();
      return this.redraw();
    };
    MapBuilder.prototype.at = function(x, y) {
      return this.rows[y][x];
    };
    MapBuilder.prototype.load_data = function() {
      this.data = json(this.e.find(".data"));
      if (!this.data) {
        return;
      }
      this.width = this.data.width;
      return this.height = this.data.height;
    };
    MapBuilder.prototype.draw_walls = function() {
      var x, y, _i, _len, _ref, _ref2, _ref3, _results;
      _ref = this.data.walls;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        _ref2 = _ref[_i], x = _ref2[0], y = _ref2[1];
        _results.push((_ref3 = this.at(x, y)) != null ? _ref3.be_wall() : void 0);
      }
      return _results;
    };
    MapBuilder.prototype.setup_form = function() {
      this.form = this.e.find("form");
      return this.form.find(":submit").click(__bind(function() {
        return this.form.find("#map_builder_data").val(JSON.stringify(this.to_json()));
      }, this));
    };
    MapBuilder.prototype.create_grid = function() {
      var box, boxes, div, i, j, row, _results;
      this.rows = [];
      i = 0;
      _results = [];
      while (i < this.height) {
        row = $("<div>");
        this.grid.append(row);
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
        return this.be_wall();
      }, this));
    }
    Box.prototype.be_wall = function() {
      return this.box.toggleClass("wall");
    };
    Box.prototype.position = function() {
      return [this.x, this.y];
    };
    Box.prototype.is_wall = function() {
      return this.box.hasClass("wall");
    };
    return Box;
  })();
}).call(this);
