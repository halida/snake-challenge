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

var room = -1;

function run_application(r){
  room = r;
  canvas = $("#canvas")[0];
  ctx = canvas.getContext("2d");

  ws = new WebSocket("ws://localhost:9999/info");
  ws.onmessage = function (e) {
      msg(data);
      var data = $.parseJSON(e.data);

      switch (data.op)
	  {
	  case 'info': 
	      pull_info(data);
	      break;
	  case 'add':
	      seq = data.seq;
	      snake_id = data.id;
	      $('#user-control-panel').show();
	      break;
	  }
  };  

  ws.onclose = function(){
      alert('connection closed, refresh please..')
  };
  ws.onopen = function(){
      ws.send('room:' + room);
  };

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
    score_board_html += '<li class="' + (snake.alive ? snake.type : 'grey' ) + '"><img src="/assets/icons/' + snake.type + color_index + '.gif" /><h2>' + snake.name + '</h2><div class="step"><font>' + snake.body.length + '</font></div></li>';
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

function pull_info(info) {
    if(finished) {
	if(info.status != 'finished') {
	    setup_walls_data();
	    finished = false;
	}
    }else{
	update(info);
	finished = info.status == 'finished';
    }
}

$(function(){
  if($("#canvas")[0]) {
    $.ajaxSetup({cache: false});
    setup_walls_data();
  }
})


var snake_id=[];
var seq=-1;
function addUser(name, type){
    ws.send(JSON.stringify({op: 'add', room: room, name: name, type: type}));
}
function turn(direction){
    if (seq <0) return;
    ws.send(JSON.stringify({
		op: 'turn',
                id: snake_id,
		snake_id:snake_id,
                room: room,
		direction: direction,
		round: -1
		}));
}
function msg(m){
    $('#debug-msg').text(m);
}

//-----------------------------------------------------
//chats
var chat_ws = [];

function append(msg){
    $('#msgs').prepend(msg);
    $('#msgs').prepend('<br/>');    
}

function chat_init(name, room){

    chat_ws = new WebSocket("ws://localhost:9999/chatroom");  

    chat_ws.onopen = function() {  
	chat_ws.send(JSON.stringify({name:name, room:room}));
    };  
    chat_ws.onmessage = function (e) {
	append(e.data); 
    };  
    chat_ws.onclose = function() { append('closed')};  

    $('#send-msg').show(200);
    $('#msg').focus();
}

function send(){
    var msg = $('#msg').val();
    chat_ws.send(JSON.stringify({msg:msg}));
    $('#msg').val('');
}

