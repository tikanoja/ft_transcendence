import time
#import threading
#import asyncio
import ssl
from flask import Flask #, render_template
from flask_socketio import SocketIO, emit


# global stuff like locks and game objects
# need to be golab because need to be
# in same process and backgroud thread + ws
# need access to same stuff
#import globals
from globals import socketio
from globals import app

# own function that sets game data ready
from set_game_settings import set_game_settings

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

# class StartGame(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 1:
# 				return jsonify({'status': 'error: game already running cannot create new'})
# 			else:
# 				games[number].set_game_running(1)
# 				games[number].new_game_initilization()
# 				games[number].set_game_slot(number)
# 				return jsonify({'status': 'ok: game running {}'.format(number)})

# class StopGame(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so cannot stop existing game'})
# 			else:
# 				games[number].set_game_running(0)
# 				games[number].set_game_slot(-1)
# 				return jsonify({'status': 'ok: game stopped {}'.format(number)})

# class GetState(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no state'})
# 			else:
# 				state = games[number].return_game_state()
# 				return jsonify({'status': 'ok: ' + str(state)})

# class StopBackgroundLoop(Resource):
# 	def get(self):
# 		global thread
# 		global thread_lock
# 		global back_ground_thread_running
# 		with thread_lock:
# 			if thread == 0:
# 				return jsonify({'status': 'error: game_loop already stopped'})
# 			else:
# 				back_ground_thread_running = 0
# 				thread = 0
# 				return jsonify({'status': 'ok: game_loop stopped'})

# class GamesRunning(Resource):
# 	def get(self):
# 		global games
# 		global games_lock
# 		games_running = ['0','0','0','0']
# 		with games_lock:
# 			for index in range(4):
# 				if games[index].game_running == 1:
# 					games_running[index] = '1'
# 		return jsonify({'status': 'ok: {}'.format(str(','.join(games_running)))})

# class LeftPaddleUp(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].left_paddle_pressed_up()
# 				return jsonify({'status': 'ok: left paddle pressed up'})

# class LeftPaddleDown(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].left_paddle_pressed_down()
# 				return jsonify({'status': 'ok: left paddle pressed down'})

# class LeftPaddleDownRelease(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].left_paddle_released_down()
# 				return jsonify({'status': 'ok: left paddle released down'})

# class LeftPaddleUpRelease(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].left_paddle_released_up()
# 				return jsonify({'status': 'ok: left paddle released up'})

# class RightPaddleUp(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].right_paddle_pressed_up()
# 				return jsonify({'status': 'ok: right paddle pressed up'})

# class RightPaddleDown(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].right_paddle_pressed_down()
# 				return jsonify({'status': 'ok: right paddle pressed down'})

# class RightPaddleDownRelease(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].right_paddle_released_down()
# 				return jsonify({'status': 'ok: right paddle released down'})

# class RightPaddleUpRelease(Resource):
# 	def get(self,number):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 0:
# 				return jsonify({'status': 'error: game not running so no keypresses'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].right_paddle_released_up()
# 				return jsonify({'status': 'ok: right paddle released up'})

# query in which slots games are running
#api.add_resource(GamesRunning, '/games_running')

# start game in specific slot
#api.add_resource(StartGame, '/game_start/<int:number>')
#api.add_resource(StopGame, '/game_stop/<int:number>')

# for debugging only get state of specific game when it is running
# oherwise error
#api.add_resource(GetState, '/game_state/<int:number>')

# this needs to be running in the background so that games update their states
# and send them to frontend
#api.add_resource(StartBackgroundLoop, '/start_background_loop')
#api.add_resource(StopBackgroundLoop, '/stop_background_loop')

# left paddle in specific game
#api.add_resource(LeftPaddleUp, '/left_paddle_up/<int:number>')
#api.add_resource(LeftPaddleUpRelease, '/left_paddle_up_release/<int:number>')
#api.add_resource(LeftPaddleDown, '/left_paddle_down/<int:number>')
#api.add_resource(LeftPaddleDownRelease, '/left_paddle_down_release/<int:number>')

# right paddle in specific game
#api.add_resource(RightPaddleUp, '/right_paddle_up/<int:number>')
#api.add_resource(RightPaddleUpRelease, '/right_paddle_up_release/<int:number>')
#api.add_resource(RightPaddleDown, '/right_paddle_down/<int:number>')
#api.add_resource(RightPaddleDownRelease, '/right_paddle_down_release/<int:number>')

#async def main():
#	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#	ssl_context.load_cert_chain("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key")
#	async with serve(echo, "localhost", 8080, ssl=ssl_context):
#		await asyncio.Future()  # stay running

#@app.route('/')
#def index():
#    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
	print('Client connected')
	socketio.emit('message', 'hello client') # {'data': 'Server says: Client connected'})
    #socketio.emit('server_says_client_connected')

@socketio.on('disconnect')
def handle_disconnect():
	print('Client disconnected')

@socketio.on('message')
def handle_message(message):
	print('Message:', message)
	socketio.emit('message', 'Server received your message: ' + message)
	splitted_command = message.split(",")
	if splitted_command:
		match splitted_command[0]:
			case 'start_background_loop':
				start_background_loop(splitted_command)
			case 'set_game_settings':
				set_game_settings(splitted_command)
			case "pattern-2":
				pass
			case _:
				socketio.emit('message', 'ERROR, Command not recognised: ' + message)
	else:
		socketio.emit('message', 'ERROR, nothing was sent.')

if __name__ == '__main__':
    # Use SSL/TLS encryption for WSS
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # ssl_context.load_cert_chain('/server.crt', '/server.key')
    socketio.run(app, host='0.0.0.0', port=8888, debug=True, allow_unsafe_werkzeug=True)
