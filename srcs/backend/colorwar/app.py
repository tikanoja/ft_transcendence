import time
import threading
import ssl
import random
from typing import Optional
from dataclasses import dataclass
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
#import sys

app = Flask(__name__)
#CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True) # works https://piehost.com/socketio-tester
#CORS(app,resources={r"/*":{"origins":"*"}}) # works https://piehost.com/socketio-tester
CORS(app) # works https://piehost.com/socketio-tester
#cors = CORS(app,resources={r"/*":{"origins":"*"}})

socketio = SocketIO(app, cors_allowed_origins="*")
#socketio = SocketIO(app)

app.debug = True
app.host = '0.0.0.0'

@dataclass
class Square:
	colour: int = 0
	owner: int = 0
	used: bool = False

class Game:
	def __init__(self):
		self.screen_width: int = 1920 # x width
		self.screen_height: int = 1080 # y height
		self.width: int = 36 # x squares
		self.height: int = 19 # y squares
		self.squares = [Square(random.choice([1, 2, 3, 4]), 0) for i in range(self.width * self.height)]
		self.which_player_starts: int = random.choice([0, 1])
		self.which_player_turn: int = self.which_player_starts
		self.allowed_colours = [1, 2, 3, 4] # white, black, green, red
		self.start_x: int = 0
		self.start_y: int = self.height // 2
		self.game_running: int = 0
		self.game_slot: int = -1
		self.left_score: int = 0
		self.right_score: int = 0
		self.moves: int = 0

	def which_player_turn(self):
		return self.which_player_turn

	def is_game_running(self):
		return self.game_running

	def set_game_running(self, running_or_not):
		self.game_running = running_or_not

	def set_game_slot(self, number):
		self.game_slot = number

	def clear_scores(self):
		self.left_score = 0
		self.right_score = 0

	def new_game_initilization(self):
		self.clear_scores()
		self.moves = 0
		self.squares = [Square(random.choice([1, 2, 3, 4]), 0) for i in range(all.width * all.height)] # Create new empty game
		self.squares[0 + (all.width * (all.height // 2))].owner = 1 # left player starting square owner to 1
		self.squares[0 + (all.width * (all.height // 2)) + all.width - 1].owner = 2 # right starting player square owner to 2
		self.which_player_starts: int = random.choice([0, 1])
		self.which_player_turn: int = which_player_starts

	#def compute_scores(self):


	def return_game_state(self):
		# self.screen_width: int = 1920 # x
		# self.screen_height: int = 1080 # y
		state = str(self.game_slot)
		state += ','
		state += str(self.left_score)
		state += ','
		state += str(self.right_score)
		state += ','
		state += str(self.game_running)
		state += ','
		state += str(self.moves)
		for y in range(all.height):
			for x in range(all.width):
				state += ','
				state += str(self.squares[x + (y * self.width)].colour) # 1,2,3,4 # white,black,green,red
				state += ','
				state += str(self.squares[x + (y * self.width)].owner) # 1,2,0 # left,right,no one owns
		return state

games_lock = threading.Lock()
with games_lock:
	games = [0,1,2,3]
	games[0] = Game()
	games[1] = Game()
	games[2] = Game()
	games[3] = Game()

# string format is set_game_settings,game_number(0,1,2,3),left_player_id(any string)
# set_game_settings,0,player1,player2,127.0.0.1,80,127.0.0.1,80 
def set_game_settings(splitted_command):
	global socketio
	global games
	global games_lock
	if len(splitted_command) != 8:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if (number < 0) or (number > 3):
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 1:
			socketio.emit('message', 'ERROR, game already running.')
			return
		else:
			games[number].left_player_id = splitted_command[2]
			games[number].right_player_id = splitted_command[3]
			socketio.emit('message', 'OK, game settings set.')
			return

def start_game(splitted_command):
	global socketio
	global games_lock
	global games
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = -1
	with games_lock:
		for index in range(4):
			if games[index].is_game_running == 0:
				number = index
				break
	with games_lock:
		if number == -1:
			socketio.emit('message', 'ERROR, game already running cannot create new.')
			return
		else:
			games[number].new_game_initilization()
			games[number].set_game_slot(number)
			games[number].set_game_running(1)
			socketio.emit('message', 'OK,{}'.format(number) + str(games[number].which_player_turn()))

def stop_game(splitted_command):
	global socketio
	#	global thread_lock
	#global thread
	global games_lock
	global games
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	with thread_lock:
		if not thread:
			socketio.emit('message', 'ERROR, background loop not running.')
			return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR: allowed game numbers are 0 to 3')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so cannot stop existing game.')
			return
		else:
			games[number].set_game_running(0)
			games[number].set_game_slot(-1)
			socketio.emit('message', 'OK, game stopped {}'.format(number))
			return

def get_state(splitted_command):
	global socketio
	global games_lock
	global games
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no state.')
			return
		else:
			socketio.emit('state', games[number].return_game_state())
			return

def	games_running(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	games_running = ['0','0','0','0']
	with games_lock:
		for index in range(4):
			if games[index].is_game_running() == 1:
				games_running[index] = '1'
	socketio.emit('message', 'OK,{}'.format(str(','.join(games_running))))
	return

def make_move(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 3:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	colour = int(splitted_command[2])
	if colour < 1 or colour > 4:
		socketio.emit('message', 'ERROR, allowed game colours are 1 to 4.')
		return
	if games[number].which_player_turn() == 0:
		games[number].start_x = 0
	else:
		games[number].start_x = all.width - 1
	for i in range(len(games[number].squares)):
		games[number].squares[i].used = False
	paint_with_colour(games[number].start_x, games[number].start_y, colour, games[number])
	games[number].which_player_turn += 1
	games[number].which_player_turn %= 2
	if check_game_running_conditions(games[number].squares):
		socketio.emit('state', 'OK,{}'.format(games[number].return_game_state()))
	else:
		games[game].set_game_running(0)
		games[number].set_game_slot(-1)
		socketio.emit('endstate', 'OK,{}'.format(games[number].return_game_state()))

@socketio.on('connect')
def handle_connect():
	#print('Client connected')
	global socketio
	socketio.emit('message', 'hello client')

@socketio.on('disconnect')
def handle_disconnect():
	#print('Client disconnected')
	pass

@socketio.on('message')
def handle_message(message):
	global socketio
	socketio.emit('message', 'Server received your message: ' + message)
	splitted_command = message.split(",")
	if splitted_command:
		match splitted_command[0]:
			case 'set_game_settings':
				set_game_settings(splitted_command)
			case 'start_game':
				start_game(splitted_command)
			case 'stop_game':
				stop_game(splitted_command)
			case 'get_state':
				get_state(splitted_command)
			case 'games_running':
				games_running(splitted_command)
			case 'make_move':
				make_move(splitted_command)
			case _:
				socketio.emit('message', 'ERROR, command not recognised: ' + message)
	else:
		socketio.emit('message', 'ERROR, nothing was sent.')

def check_game_running_conditions(squares):
	total_squares = all.width * all.height
	half_squares = int(total_squares / 2)
	# player 1 squares
	total_player_squares = int(0)
	for i in all.squares:
		if i.owner == 1:
			total_player_squares += 1
	if total_player_squares > half_squares:
		return False
	# player 2 squares
	total_player_squares = int(0)
	for i in all.squares:
		if i.owner == 2:
			total_player_squares += 1
	if total_player_squares > half_squares:
		return False
	# if no player has more than 50 percent of squares
	# then check if there are are still unclaimed squares
	for i in all.squares:
		if i.owner == 0:
			return True
	return False

def return_owner(x, y, game):
	return game.squares[x + (y * game.width)].owner

def return_colour(x, y, game):
	return  game.squares[x + (y * game.width)].colour

def set_colour(x, y, colour, game):
	all.squares[x + (y * game.width)].colour = colour

def return_used(x, y, game):
	return game.squares[x + (y * game.width)].used

def set_used(x, y, game):
	game.squares[x + (y * game.width)].used = True

def paint_with_colour(x, y, colour, game):
	if x < 0 or x >= game.width: # out of bounds
		return
	if y < 0 or y >= game.height: # out of bounds
		return
	if return_used(x, y, game) == True:
		return
	if return_owner(x, y, game) == game.which_player_turn + 1: # is the owner, print with new colour
		set_colour(x, y, colour, game)
		set_used(x, y, game)
		paint_with_colour(x + 1, y, colour, game)
		paint_with_colour(x - 1, y, colour, game)
		paint_with_colour(x, y + 1, colour, game)
		paint_with_colour(x, y - 1, colour, game)
		return
	if return_owner(x, y, game) == 0 and return_colour(x, y, game) == colour: # no one owns and the colour matches
		game.squares[x + (y * all.width)].owner = game.which_player_turn + 1
		set_used(x, y, game)
		paint_with_colour(x + 1, y, colour, game)
		paint_with_colour(x - 1, y, colour, game)
		paint_with_colour(x, y + 1, colour, game)
		paint_with_colour(x, y - 1, colour, game)

def who_won_or_draw(game):
	total_squares = all.width * all.height
	half_squares = int(total_squares / 2)
	# player 1 squares
	total_player_squares1 = int(0)
	for i in game.squares:
		if i.owner == 1:
			total_player_squares1 += 1
	if total_player_squares1 > half_squares:
		return 1 # player 1
	# player 2 squares
	total_player_squares2 = int(0)
	for i in game.squares:
		if i.owner == 2:
			total_player_squares2 += 1
	if total_player_squares2 > half_squares:
		return 2 # player 2
	# Draw
	if total_player_squares1 == total_player_squares2:
		return 0 # draw
	
if __name__ == '__main__':
	# Use SSL/TLS encryption for WSS
	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ssl_context.load_cert_chain('/server.crt', '/server.key')
	socketio.run(app, host='0.0.0.0', port=8889, debug=True, ssl_context=ssl_context, allow_unsafe_werkzeug=True)
	#socketio.run(app, host='0.0.0.0', port=8889, debug=True, allow_unsafe_werkzeug=True)
