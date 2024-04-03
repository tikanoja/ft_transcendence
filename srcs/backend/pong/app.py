
import time
import threading
#import random
import asyncio
import websockets
import ssl
from websockets.server import serve

# own dataclass = c++ struct
#from GameObject import GameObject

# own class that holds all game data
from Game import Game

games_lock = threading.Lock()
games = [0,1,2,3]
with games_lock:
	games[0] = Game()
	games[1] = Game()
	games[2] = Game()
	games[3] = Game()

thread = 0
thread_lock = threading.Lock()
with thread_lock:
	back_ground_thread_running = 0

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

# class StartBackgroundLoop(Resource):
# 	def get(self):
# 		global thread
# 		global thread_lock
# 		global back_ground_thread_running
# 		with thread_lock:
# 			if thread != 0:
# 				return jsonify({'status': 'error: game_loop already running'})
# 			else:
# 				back_ground_thread_running = 1
# 				thread = threading.Thread(target=game_loop)
# 				thread.start()
# 				return jsonify({'status': 'ok: game_loop started'})

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

# class LeftPlayerId(Resource):
# 	def get(self,number,id):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 1:
# 				return jsonify({'status': 'error: game running so changing id'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].left_player_id = id
# 				return jsonify({'status': 'ok: left player id set'})

# class RightPlayerId(Resource):
# 	def get(self,number,id):
# 		global games
# 		global games_lock
# 		if number < 0 or number > 3:
# 			return jsonify({'status': 'error: allowed game numbers are 0 to 3'})
# 		with games_lock:
# 			if games[number].is_game_running() == 1:
# 				return jsonify({'status': 'error: game running so changing id'})
# 			else:
# 				#return jsonify({'status': 'ok: ' + str(state)})
# 				games[number].right_player_id = id
# 				return jsonify({'status': 'ok: left player id set'})

# query in which slots games are running
#api.add_resource(GamesRunning, '/games_running')

# set set player id when game is not running
# otherwise error
#api.add_resource(LeftPlayerId, '/left_player_id/<int:number>/<string:id>')
#api.add_resource(RightPlayerId, '/right_player_id/<int:number>/<string:id>')

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

# async def echo(websocket, path):
# 	async for message in websocket:
# 		#print(f"Received message from client: {message}")
# 		await websocket.send(f"Hello, Client! You said: {message}")

#async def main():
#	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#	ssl_context.load_cert_chain("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key")
#	async with serve(echo, "localhost", 8080, ssl=ssl_context):
#		await asyncio.Future()  # stay running

# async def main():
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     try:
#         ssl_context.load_cert_chain("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key")
#     except Exception as e:
#         print("Error loading SSL certificate:", e)
#         return

#     if ssl_context.certfile and ssl_context.keyfile:
#         print("SSL certificate loaded successfully.")
#     else:
#         print("SSL certificate loading failed.")
#         return

#     async with serve(echo, "localhost", 8080, ssl=ssl_context):
#         await asyncio.Future()  # stay running

# async def main():
# 	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# 	try:
# 		ssl_context.load_cert_chain("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key")
# 	except Exception as e:
# 		print("Error loading SSL certificate:", e)
# 		sys.exit()
# 		return

# 	print("SSL certificate loaded successfully.")

# 	async with serve(echo, "localhost", 8080, ssl=ssl_context):
# 		await asyncio.Future()  # stay running

#if __name__ == '__main__':
	#asyncio.run(main())

	#app.run(debug=False, threaded=False) #flask

	#start_server = websockets.serve(mainecho, "localhost", 8765) # alt staty running forever async
	#asyncio.get_event_loop().run_until_complete(start_server)
	#asyncio.get_event_loop().run_forever()

# import asyncio
# import ssl

# import websockets

# async def echo(websocket, path):
#     async for message in websocket:
#         print(f"Received message from client: {message}")
#         await websocket.send(f"Hello, Client! You said: {message}")

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# try:
# 	ssl_context.load_cert_chain("/server.crt", "/server.key")
# except Exception as e:
# 	print("Error loading SSL certificate:", e)
# 	sys.exit()

# #ssl_context.load_cert_chain("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key")
# start_server = websockets.serve(echo, "127.0.0.1", 8888, ssl=ssl_context)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()

import asyncio
import ssl
import websockets

# async def main(websocket, path):
# 	async for message in websocket:
# 		splitted_command = message.split(",")
# 		if splitted_command.empty() :
# 			match splitted_command[0]:
# 				case pattern-1:
#          			action-1
# 				case "pattern-2":
# 					pass
# 				case "pattern-3":
# 					pass
# 				case _:
# 					await websocket.send(f"Hello, Client! You said: {message}")

async def main(websocket, path):
	async for message in websocket:
		await websocket.send(f"Hello, Client! You said: {message}")

async def starter_main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain("/server.crt", "/server.key")  # Replace with your SSL certificate and key path

    async with websockets.serve(main, "0.0.0.0", 8888, ssl=ssl_context):
        await asyncio.Future()  # Run forever

asyncio.run(starter_main())
