import threading
import globals

def stop_background_loop(splitted_command):
	with globals.thread_lock:
		if globals.background_thread_running == 0:
			globals.socketio.emit('message', 'ERROR, game loop already stopped.')
			#return jsonify({'status': 'error: game_loop already stopped'})
		else:
			globals.background_thread_running = 0
			globals.thread = None
			globals.socketio.emit('message', 'OK, gameloop stopped.')
			#return jsonify({'status': 'ok: game_loop stopped'})
