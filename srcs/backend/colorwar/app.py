import time
import threading
import ssl
import random
from typing import Optional
from dataclasses import dataclass
from flask import Flask #, render_template
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
		#main: int = 0
		#canvas: int = 0
		#rectangle_width: int = 50
		#rectangle_height: int = 50
		screen_width: int = 1920 # x width
		screen_height: int = 1080 # y height
		width: int = 36
		height: int = 19
		squares = [Square(random.choice([1, 2, 3, 4]), 0) for i in range(all.width * all.height)]
		which_player_starts: int = random.choice([0, 1])
		which_player_turn: int = which_player_starts
		allowed_colours = [1, 2, 3, 4] # white, black, green, red
		start_x: int = 0
		start_y: int = height // 2
		game_running: int = 0
		game_slot: int = -1
		left_score: int = 0
		right_score: int = 0
		moves: int = 0

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

	# if (self.left_score or self.right_score) >= self.game_end_condition:
	# 	self.game_running = 0
	# 	self.ball_bounces = 0
	# 	self.winner = "left player"
	# 	if self.right_score > self.left_score:
	# 		self.winner = "right player"

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
		return state

games_lock = threading.Lock()
with games_lock:
	games = [0,1,2,3]
	games[0] = Game()
	games[1] = Game()
	games[2] = Game()
	games[3] = Game()

#thread = None
#thread_lock = threading.Lock()
#with thread_lock:
#	background_thread_running = 0
# def game_loop:
# 	# yes it needs to be running even when games are not running
# 	# so it will be ready when game start
# 	global background_thread_running
# 	global games_lock
# 	global games
# 	global socketio
# 	while True:
# 		if background_thread_running == 0:
# 			return
# 		with games_lock:
# 			for game in range(4):
# 				if games[game].is_game_running() == 1:
# 					games[game].move_paddles()
# 					games[game].move_ball()
# 					socketio.emit('state', games[game].return_game_state())
# 		time.sleep(0.02)

# def start_background_loop(splitted_command):
# 	global thread
# 	global thread_lock
# 	global socketio
# 	global background_thread_running
# 	if len(splitted_command) != 1:
# 		socketio.emit('message', 'ERROR, string not in right format.')
# 		return
# 	with thread_lock:
# 		if thread:
# 			socketio.emit('message', 'ERROR, background loop already running.')
# 			return
# 		else:
# 			background_thread_running = 1
# 			thread = threading.Thread(target=game_loop)
# 			thread.start()
# 			socketio.emit('message', 'OK: background loop started.')
# 			return

# def stop_background_loop(splitted_command):
# 	global thread
# 	global thread_lock
# 	global background_thread_running
# 	global socketio
# 	if len(splitted_command) != 1:
# 		socketio.emit('message', 'ERROR, string not in right format.')
# 		return
# 	with thread_lock:
# 		if background_thread_running == 0:
# 			socketio.emit('message', 'ERROR, game loop already stopped.')
# 			return
# 		else:
# 			background_thread_running = 0
# 			thread = None
# 			socketio.emit('message', 'OK, gameloop stopped.')
# 			return

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
	#global thread_lock
	#global thread
	global games_lock
	global games
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	#with thread_lock:
	#	if not thread:
	#		socketio.emit('message', 'ERROR, background loop not running.')
	#		return
	number = -1
	with games_lock:
		for index in range(4):
			if games[index].is_game_running == 0
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
			return

def stop_game(splitted_command):
	global socketio
	global thread_lock
	global thread
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
	socketio.emit('message', 'OK, {}'.format(str(','.join(games_running))))
	return

# #@app.route('/')
# #def index():
# #    return render_template('index.html')

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
			#case 'start_background_loop':
			#	start_background_loop(splitted_command)
			#case 'stop_background_loop':
			#	stop_background_loop(splitted_command)
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
			case _:
				socketio.emit('message', 'ERROR, command not recognised: ' + message)
	else:
		socketio.emit('message', 'ERROR, nothing was sent.')

# if __name__ == '__main__':
# 	# Use SSL/TLS encryption for WSS
# 	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# 	ssl_context.load_cert_chain('/server.crt', '/server.key')
# 	socketio.run(app, host='0.0.0.0', port=8888, debug=True, ssl_context=ssl_context, allow_unsafe_werkzeug=True)
# 	#socketio.run(app, host='0.0.0.0', port=8888, debug=True, allow_unsafe_werkzeug=True)

# def pretty_print_game_board(squares):
# 	for y in range(all.height):
# 		for x in range(all.width):
# 			print('(', end='')
# 			print(squares[x + (y * all.width)].colour, end='')
# 			print(',', end='')
# 			print(squares[x + (y * all.width)].owner, end='')
# 			print(')', end='')
# 		print('')

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

def return_owner(x, y, all):
	return all.squares[x + (y * all.width)].owner

def return_colour(x, y, all):
	return  all.squares[x + (y * all.width)].colour

def set_colour(x, y, colour, all):
	all.squares[x + (y * all.width)].colour = colour

def return_used(x, y, all):
	return all.squares[x + (y * all.width)].used

def set_used(x, y, all):
	all.squares[x + (y * all.width)].used = True

def paint_with_colour(x, y, colour, all):
	if x < 0 or x >= all.width: # out of bounds
		return
	if y < 0 or y >= all.height: # out of bounds
		return
	if return_used(x, y, all) == True:
		return
	if return_owner(x, y, all) == all.which_player_turn + 1: # is the owner, print with new colour
		set_colour(x, y, colour, all)
		set_used(x, y, all)
		#print("owner")
		#print(return_colour(x, y, all))
		paint_with_colour(x + 1, y, colour, all)
		paint_with_colour(x - 1, y, colour, all)
		paint_with_colour(x, y + 1, colour, all)
		paint_with_colour(x, y - 1, colour, all)
		return
	if return_owner(x, y, all) == 0 and return_colour(x, y, all) == colour: # no one owns and the colour matches
		all.squares[x + (y * all.width)].owner = all.which_player_turn + 1
		set_used(x, y, all)
		paint_with_colour(x + 1, y, colour, all)
		paint_with_colour(x - 1, y, colour, all)
		paint_with_colour(x, y + 1, colour, all)
		paint_with_colour(x, y - 1, colour, all)
 
def player_move(colour, all):
	if all.which_player_turn == 0:
		all.start_x = 0
		#print("player 1")
		#original_colour = squares[0 + (width * (height // 2))].colour
	else:
		#print("player 2")
		all.start_x = all.width - 1
		#original_colour = squares[0 + (width * (height // 2)) + width - 1].colour
	for i in range(len(all.squares)):
		all.squares[i].used = False
	#print("x and y")
	#print(all.start_x, all.start_y)
	paint_with_colour(all.start_x, all.start_y, colour, all)

def initialize_and_return_Game():
	all.characters = [0] * (all.height * all.width)
	for i in range(all.height * all.width):
		character = ''
		if all.squares[i].owner == 1:
			character = '1'
		elif all.squares[i].owner == 2:
			character = '2'
	return all

def who_won_or_draw(all):
	total_squares = all.width * all.height
	half_squares = int(total_squares / 2)

	# player 1 squares
	total_player_squares1 = int(0)
	for i in all.squares:
		if i.owner == 1:
			total_player_squares1 += 1
	if total_player_squares1 > half_squares:
		print("Player 1 wins")
		return

	# player 2 squares
	total_player_squares2 = int(0)
	for i in all.squares:
		if i.owner == 2:
			total_player_squares2 += 1
	if total_player_squares2 > half_squares:
		print("Player 2 wins")
		return

	if total_player_squares1 == total_player_squares2:
		print("Draw")
		return
	
if __name__ == '__main__':
	
	all = initialize_and_return_all()

	while(check_game_running_conditions(all.squares)):
		pretty_print_game_board(all.squares)
		if all.which_player_turn == 0:
			try:
				num_input = int(input_text)
			except:
				num_input = -1
		else:
			try:
				num_input = int(input_text)
			except:
				num_input = -1

		if num_input not in all.allowed_colours:
			continue
		else:
			if all.which_player_turn == 0:
				player_move(num_input, all)
			else:
				player_move(num_input, all)
		all.which_player_turn +=1
		all.which_player_turn %= 2

	#pretty_print_game_board(all.squares)
	#who_won_or_draw(all)
