var walls = [];
var scale = 15;
var colors = {
    "wall": "#8c8c8c",
    "python": [["#a5c9e7", "#08467b", "#3e9be9"],["#88db99", "#0e7483", "#85f56b"],["#a5c9e7", "#0a4846", "#3ae712"],["#88db99", "#f3f00a", "#0db02c"]],
    "ruby": [["#eb88a9", "#b30c43", "#f81919"],["#f45e5e", "#83103e", "#e07711"],["#eb88a9", "#8151a6", "#59edef"],["#f45e5e", "#f8952a", "#ffea00"]],
    "dead": ["#8c8c8c", "#8c8c8c", "#8c8c8c"]
};
var score_board_html = "";
var finished = false;
var canvas;
var ctx;

function run_application(){
  canvas = $("#canvas")[0];
  ctx = canvas.getContext("2d");
}

function update(info) {
    //clear canvas and score board html
    canvas.width = canvas.width;
    score_board_html = "";

    //draw walls
    draw_walls();

    //update round and status
    $('#round_counter').html(info.round + ' ' + info.status);

    //draw snake and update score board
    $.each(info.snakes.sort(function(a, b) {
        return b.body.length - a.body.length;
    }), function(index) {
        draw_snake(this, index % 4);
    });

    $('#score_board').html(score_board_html);

    //draw eggs and gems
    $.each(info.eggs, function() {
        draw_egg(this);
    })

    $.each(info.gems, function() {
        draw_gem(this);
    })
}

function draw_snake(snake, color_index) {
    color_set = snake.alive ? colors[snake.type][color_index] : colors.dead;
    //draw body
    ctx.fillStyle = color_set[0];
    $.each(snake.body, function() {
        ctx.fillRect(this[0] * scale, this[1] * scale, scale, scale);
    })

    //draw head and eye
    var head = snake.body[0];
    ctx.fillStyle = color_set[1];
    ctx.fillRect(head[0] * scale, head[1] * scale, scale, scale);
    ctx.fillStyle = color_set[2];
    ctx.fillRect(head[0] * scale + 4, head[1] * scale + 4, scale - 8, scale - 8);

    //add to score board
    score_board_html += '<li class="' + (snake.alive ? snake.type : 'grey' ) + '"><img src="/images/icons/' + snake.type + color_index + '.gif" /><h2>' + snake.name + '</h2><div class="step"><font>' + snake.body.length + '</font></div></li>';
}

function draw_egg(egg) {
    ctx.drawImage(document.getElementById("icon_egg"), egg[0] * scale, egg[1] * scale);
}

function draw_gem(gem) {
    ctx.drawImage(document.getElementById("icon_gem"), gem[0] * scale, gem[1] * scale);
}

function draw_walls() {
    ctx.fillStyle = colors.wall;
    $.each(walls, function() {
        ctx.fillRect(this[0] * scale, this[1] * scale, scale, scale);
    });
}

function setup_walls_data() {
    $.getJSON('map', function(map) {
        walls = map.walls;
    });
}

function pull_info() {
    $.getJSON('info', function(info) {
        //wait 0.6 second to pull info again
        setTimeout(function() {
            pull_info();
        }, 600);
        
        if(finished) {
            if(info.status != 'finished') {
                setup_walls_data();
                finished = false;
            }
        }else{
            update(info);
            finished = info.status == 'finished';
        }
    });
}

$(function(){
  if($("#canvas")[0]) {
    $.ajaxSetup({cache: false});
    setup_walls_data();
    pull_info();
  }
})


var snake_id=[];
var seq=-1;
function addUser(){
    $.post('./add', {name: 'fucker',
		     type: 'python'},
	   function(data){
	       msg(data);
	       data = $.parseJSON(data);
	       seq = data.seq;
	       snake_id = data.id;
	       $('#user-control-panel').show();
	   });
}
function turn(direction){
    if (seq <0) return;
    $.post('./turn', {snake_id:snake_id,
		      direction: direction,
		      round: -1
		     },
	   function(data){
	       msg(data);
	   });
}
function msg(m){
    $('#msg').text(m);
}
