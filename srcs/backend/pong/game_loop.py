import threading

from globals import games
from globals import games_lock
from globals import back_ground_thread_running 

def game_loop():
	# this is backgroung thread that is lurking in the background
	# it needs to be started before setting up games
	# yes it needs to be running even when games are not running
	# so it will be ready when game start
	global games
	global games_lock
	global back_ground_thread_running
	while True:
		if back_ground_thread_running == 0:
			return
		with games_lock:
			for game in range(4):
				if games[game].is_game_running() == 1:
					games[game].move_paddles()
					games[game].move_ball()
		time.sleep(0.02)
