#-*- coding:utf-8 -*-
unittest:
	python srcs/snake_game.py
	python srcs/game_controller.py
	python srcs/ailib.py

# run the game server
game:
	python srcs/zmq_game_server.py 4webai
# run the web server
web:
	cd rubyweb; ruby server.rb
# run a test ai
ai:
	python srcs/ai_simple.py zero 0

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
