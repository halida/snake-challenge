#-*- coding:utf-8 -*-
unittest:
	python srcs/snake_game.py
	python srcs/game_controller.py
	python srcs/ailib.py

# run the game server
game:
	python srcs/zmq_game_server.py local
webgame:
	python srcs/zmq_game_server.py web

# run the website
website:
	cd rubyweb; bundle exec rails server -p 2000

# run http interface server
http:
	cd srcs; python web_server.py

# run a test ai
ai:
	python examples/ai_halida.py zero 0

# run lots of test ai
ais:
	python examples/ai_halida.py zero 0 4

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
