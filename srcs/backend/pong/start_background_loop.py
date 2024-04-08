import threading

from globals import thread
from globals import thread_lock
from globals import back_ground_thread_running 
from globals import socketio

from game_loop import game_loop

def start_background_loop(splitted_command):
	global thread
	global thread_lock
	global back_ground_thread_running
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
	with thread_lock:
		if thread != 0:
			socketio.emit('message', 'ERROR, background loop already running.')
			# return jsonify({'status': 'error: game_loop already running'})
		else:
			back_ground_thread_running = 1
			thread = threading.Thread(target=game_loop)
			thread.start()
			socketio.emit('message', 'OK: background loop started.')
			#return jsonify({'status': 'ok: game_loop started'})
