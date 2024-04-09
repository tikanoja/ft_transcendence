import threading
import globals
import game_loop

def start_background_loop(splitted_command):
	if len(splitted_command) != 1:
		globals.socketio.emit('message', 'ERROR, string not in right format.')
		return
	with globals.thread_lock:
		if globals.thread:
			globals.socketio.emit('message', 'ERROR, background loop already running.')
			return
			# return jsonify({'status': 'error: game_loop already running'})
		else:
			globals.background_thread_running = 1
			globals.thread = threading.Thread(target=game_loop.game_loop)
			globals.thread.start()
			globals.socketio.emit('message', 'OK: background loop started.')
			return
			#return jsonify({'status': 'ok: game_loop started'})
