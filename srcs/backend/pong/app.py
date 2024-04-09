import time
#import threading
#import asyncio
import ssl
from flask import Flask #, render_template
from flask_socketio import SocketIO, emit

# global stuff like locks and game objects
# need to be global because need to be
# in same process and backgroud thread + ws
# need access to same stuff
import globals

# own function
from start_background_loop import start_background_loop

# own function
from stop_background_loop import stop_background_loop

# own function
from set_game_settings import set_game_settings

# own function
from start_game import start_game

# own function
from stop_game import stop_game

# own function
from get_state import get_state

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

#@app.route('/')
#def index():
#    return render_template('index.html')

@globals.socketio.on('connect')
def handle_connect():
	print('Client connected')
	globals.socketio.emit('message', 'hello client') # {'data': 'Server says: Client connected'})
    #socketio.emit('server_says_client_connected')

@globals.socketio.on('disconnect')
def handle_disconnect():
	print('Client disconnected')

@globals.socketio.on('message')
def handle_message(message):
	print('Message:', message)
	globals.socketio.emit('message', 'Server received your message: ' + message)
	splitted_command = message.split(",")
	if splitted_command:
		match splitted_command[0]:
			case 'start_background_loop':
				start_background_loop(splitted_command)
			case 'stop_background_loop':
				stop_background_loop(splitted_command)
			case 'set_game_settings':
				set_game_settings(splitted_command)
			case "start_game":
				start_game(splitted_command)
			case "stop_game":
				stop_game(splitted_command)
			case "get_state":
				get_state(splitted_command)
			case _:
				socketio.emit('message', 'ERROR, command not recognised: ' + message)
	else:
		globals.socketio.emit('message', 'ERROR, nothing was sent.')

if __name__ == '__main__':
	# Use SSL/TLS encryption for WSS
	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ssl_context.load_cert_chain('/server.crt', '/server.key')
	globals.socketio.run(globals.app, host='0.0.0.0', port=8888, debug=True, ssl_context=ssl_context, allow_unsafe_werkzeug=True)
	#socketio.run(app, host='0.0.0.0', port=8888, debug=True, allow_unsafe_werkzeug=True)
