import globals

# string format is set_game_settings,game_number(0,1,2,3),left_player_id(any string)
# set_game_settings,0,player1,player2,127.0.0.1,80,127.0.0.1,80 
def set_game_settings(splitted_command):
	if len(splitted_command) != 8:
		globals.socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if (number < 0) or (number > 3):
		globals.socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with globals.games_lock:
		if globals.games[number].is_game_running() == 1:
			globals.socketio.emit('message', 'ERROR, game already running.')
			return
		else:
			#return jsonify({'status': 'ok: ' + str(state)})
			globals.games[number].left_player_id = splitted_command[2]
			globals.games[number].right_player_id = splitted_command[3]
			globals.socketio.emit('message', 'OK, game settings set.')
			return
			#return jsonify({'status': 'ok: left player id set'})