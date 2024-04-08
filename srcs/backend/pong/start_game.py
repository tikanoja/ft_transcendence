import globals

def start_game(splitted_command):
	if len(splitted_command) != 2:
		globals.socketio.emit('message', 'ERROR, string not in right format.')
		return
	with globals.thread_lock:
		if not globals.thread:
			globals.socketio.emit('message', 'ERROR, background loop not running.')
			return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		globals.socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
		#return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
	with globals.games_lock:
		if globals.games[number].is_game_running() == 1:
			globals.socketio.emit('message', 'ERROR, game already running cannot create new.')
			return
			#return jsonify({'status': 'error: game already running cannot create new'})
		else:
			globals.games[number].set_game_running(1)
			globals.games[number].new_game_initilization()
			globals.games[number].set_game_slot(number)
			globals.socketio.emit('message', 'OK, game running {}.'.format(number))
			return
			#return jsonify({'status': 'ok: game running {}'.format(number)})
