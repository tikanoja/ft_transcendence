import globals

def stop_game(splitted_command):
	if len(splitted_command) != 2:
		globals.socketio.emit('message', 'ERROR, string not in right format.')
		return
	with globals.thread_lock:
		if not globals.thread:
			globals.socketio.emit('message', 'ERROR, background loop not running.')
			return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		globals.socketio.emit('message', 'ERROR: allowed game numbers are 0 to 3')
		return
	with globals.games_lock:
		if globals.games[number].is_game_running() == 0:
			globals.socketio.emit('message', 'ERROR, game not running so cannot stop existing game.')
			return
		else:
			globals.games[number].set_game_running(0)
			globals.games[number].set_game_slot(-1)
			globals.socketio.emit('message', 'OK, game stopped {}'.format(number))
			return
