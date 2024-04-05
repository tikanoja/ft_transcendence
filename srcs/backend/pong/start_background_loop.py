from globals import thread
from globals import thread_lock
from globals import back_ground_thread_running 

def start_background_loop(splitted_command):
    global thread
	global thread_lock
	global back_ground_thread_running
	with thread_lock:
	    if thread != 0:
		    return jsonify({'status': 'error: game_loop already running'})
		else:
            back_ground_thread_running = 1
            thread = threading.Thread(target=game_loop)
            thread.start()
			return jsonify({'status': 'ok: game_loop started'})
