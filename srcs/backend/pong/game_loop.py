import globals

def game_loop():
	# this is backgroung thread that is lurking in the background
	# it needs to be started before setting up games
	# yes it needs to be running even when games are not running
	# so it will be ready when game start
	while True:
		if globals.background_thread_running == 0:
			return
		with globals.games_lock:
			for game in range(4):
				if globals.games[game].is_game_running() == 1:
					globals.games[game].move_paddles()
					globals.games[game].move_ball()
		time.sleep(0.02)
