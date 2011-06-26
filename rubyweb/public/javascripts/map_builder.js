(function() {
  var $, Box, Map, MapBuilder, MapPreview, exists, json;
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
  Map = (function() {
    function Map(e) {
      this.e = $(e);
    }
    Map.prototype.at = function(x, y) {
      var row;
      return (row = this.boxes[y]) && row[x];
    };
    Map.prototype.draw = function(data) {
      var grid;
      grid = this.e.find(".grid");
      if (grid.size() > 0) {
        grid.remove();
      }
      this.draw_grid(data.width, data.height);
      return this.draw_walls(data.walls);
    };
    Map.prototype.draw_walls = function(walls) {
      var x, y, _i, _len, _ref, _ref2, _results;
      _results = [];
      for (_i = 0, _len = walls.length; _i < _len; _i++) {
        _ref = walls[_i], x = _ref[0], y = _ref[1];
        _results.push((_ref2 = this.at(x, y)) != null ? _ref2.be_wall() : void 0);
      }
      return _results;
    };
    Map.prototype.draw_grid = function(w, h) {
      var div, row, x, y;
      this.grid = $("<div class='grid'>");
      this.boxes = (function() {
        var _results;
        _results = [];
        for (y = 0; 0 <= h ? y < h : y > h; 0 <= h ? y++ : y--) {
          row = $("<div class='row'>");
          this.grid.append(row);
          _results.push((function() {
            var _results2;
            _results2 = [];
            for (x = 0; 0 <= w ? x < w : x > w; 0 <= w ? x++ : x--) {
              div = $("<div class='box'>");
              row.append(div);
              _results2.push(new Box(div, x, y));
            }
            return _results2;
          })());
        }
        return _results;
      }).call(this);
      return this.e.append(this.grid);
    };
    return Map;
  })();
  MapPreview = (function() {
    function MapPreview(e) {
      this.e = $(e);
      this.data = json(this.e.find(".data"));
      this.preview = this.e.find(".preview");
      this.map = new Map(this.preview);
      this.map.draw(this.data);
    }
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
      this.data = json(this.e.find(".data"));
      this.map = new Map(this.e.find(".map"));
      this.map.draw(this.data);
    }
    MapBuilder.prototype.walls = function() {
      var box, row, walls, _i, _j, _len, _len2, _ref;
      walls = [];
      _ref = this.map.boxes;
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
        width: this._width.val(),
        height: this._height.val()
      };
    };
    MapBuilder.prototype.adjust_dimension = function() {
      return this.map.draw(this.to_json());
    };
    MapBuilder.prototype.setup_form = function() {
      this.form = this.e.find("form");
      return this.form.find(":submit").click(__bind(function() {
        return this.form.find("#map_builder_data").val(JSON.stringify(this.to_json()));
      }, this));
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
