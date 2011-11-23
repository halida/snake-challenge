#-*- coding:utf-8 -*-
unittest:
	python srcs/snake_game.py
	python srcs/game_controller.py
	python srcs/ailib.py

# run the game server
game:
	python srcs/zmq_game_server.py 4web
# run the web server
web:
	cd rubyweb; bundle exec rails server -p 2000
# run websocket server
websocket:
	cd srcs; python websocket_server.py
# run a test ai
ai:
	python srcs/ai_simple.py zero 0
# run lots of test ai
ais:
	python srcs/ai_simple.py zero 0 5

# pygame show local game
pygame:
	python srcs/pygame_show.py
show:
	python srcs/zmq_pygame_show.py 0

# record/replay log
record:
	python srcs/zmq_logger.py zero 0 test.log
replay:
	python srcs/zmq_replayer.py test.log
