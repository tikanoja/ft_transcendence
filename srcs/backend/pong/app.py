import time
import threading
import ssl
import random
from typing import Optional
from dataclasses import dataclass
from flask import Flask #, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

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
class GameObject:
    x: float
    y: float
    width: float
    height: float

class Game:
	def __init__(self):
		self.game_slot: int = -1
		self.ball_coordinates: Optional[GAmeObject.GameObject] = None # x,y,width,height
		self.ball_initial_coordinates: Optional[Gameobject.GameObject] = None # x,y,width,height
		self.left_paddle_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
		self.left_paddle_initial_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
		self.right_paddle_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
		self.right_paddle_initial_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
		self.screen_width: int = 1920 # x
		self.screen_height: int = 1080 # y
		self.screen_middle_point = [float((self.screen_width / 2)), float((self.screen_height / 2))] # [x, y]
		self.even_odd_ball_direction: int = 0 # every other times ball goes to left and then right
		self.initial_direction: int = random.choice([1, -1])
		self.ball_starting_speed = [float(7.0 * self.initial_direction), float(0)] # [x, y]
		self.ball_speed = [float(self.ball_starting_speed[0]), float(self.ball_starting_speed[1])] # [x, y]
		self.ball_speed_limit: float = 50 # both x,y
		self.ball_R: int = 25 # radius
		self.paddle_width: int = 20
		self.paddle_height: int = 90
		self.paddle_speed: int = 15
		self.paddle_distance_to_wall: int = 50
		self.w_pressed: bool = False # left up
		self.s_pressed: bool = False # left down
		self.up_pressed: bool = False # right up
		self.down_pressed: bool = False # right down
		self.left_score: int = 0 # actual score not tkinter object
		self.right_score: int = 0 # actual score not tkinter object
		self.game_end_condition: int = 3 # how many points till end
		self.game_running: int = 0 # 1 running, 0 end
		self.winner: str = 'nobody'
		self.left_player_id: str = 'left_player'
		self.right_player_id: str = 'righ_player'
		self.create_ball_initial_coordinates()
		self.create_left_paddle_initial_coordinates()
		self.create_right_paddle_initial_coordinates()

	def set_game_slot(self, number):
		self.game_slot = number

	def clear_scores(self):
		self.left_score = 0
		self.right_score = 0

	def new_game_initilization(self):
		self.clear_scores()
		self.create_ball_paddles_scoreboard()
		self.game_running = 1
		self.w_pressed = 0
		self.s_pressed = 0
		self.up_pressed = 0
		self.down_pressed = 0

	def create_ball_initial_coordinates(self):
		self.ball_initial_coordinates = GameObject(
		self.screen_middle_point[0],
		self.screen_middle_point[1],
		self.ball_R,
		self.ball_R
		)
		self.ball_coordinates = GameObject(
		self.screen_middle_point[0],
		self.screen_middle_point[1],
		self.ball_R,
		self.ball_R
    	)

	def create_left_paddle_initial_coordinates(self):
		self.left_paddle_initial_coordinates = GameObject(
		self.paddle_distance_to_wall + self.paddle_width,
		self.screen_middle_point[1],
		self.paddle_width,
		self.paddle_height
    	)
		self.left_paddle_coordinates = GameObject(
		self.paddle_distance_to_wall + self.paddle_width,
		self.screen_middle_point[1],
		self.paddle_width,
		self.paddle_height
		)

	def create_right_paddle_initial_coordinates(self):
		self.right_paddle_initial_coordinates = GameObject(
		self.screen_width - self.paddle_distance_to_wall - self.paddle_width,
		self.screen_middle_point[1],
		self.paddle_width,
		self.paddle_height
    	)
		self.right_paddle_coordinates = GameObject(
		self.screen_width - self.paddle_distance_to_wall - self.paddle_width,
		self.screen_middle_point[1],
		self.paddle_width,
		self.paddle_height
		)

	def move_paddles(self):
		# left paddle
		if self.w_pressed:
			self.left_paddle_coordinates.y -= self.paddle_speed
			if (self.left_paddle_coordinates.y - self.paddle_height) < 2:
				self.left_paddle_coordinates.y = 2 + self.paddle_height
		if self.s_pressed:
			self.left_paddle_coordinates.y += self.paddle_speed
			if self.left_paddle_coordinates.y + self.paddle_height > self.screen_height - 2:
				self.left_paddle_coordinates.y = self.screen_height - 2 - self.paddle_height
		# right paddle
		if self.up_pressed:
			self.right_paddle_coordinates.y -= self.paddle_speed
			if (self.right_paddle_coordinates.y - self.paddle_height) < 2:
				self.right_paddle_coordinates.y = 2 + self.paddle_height
		if self.down_pressed:
			self.right_paddle_coordinates.y += self.paddle_speed
			if self.right_paddle_coordinates.y + self.paddle_height > self.screen_height - 2:
				self.right_paddle_coordinates.y = self.screen_height - 2 - self.paddle_height

	def too_far_left(self):
		# too far left
		if (self.ball_coordinates.x - self.ball_coordinates.width <= self.left_paddle_coordinates.x + self.paddle_width):
			# hit left paddle
			if (self.ball_coordinates.y >= self.left_paddle_coordinates.y - self.paddle_height
				and self.ball_coordinates.y <= self.left_paddle_coordinates.y + self.paddle_height):
				self.ball_speed[0] = abs(self.ball_speed[0]) # x speed
				self.ball_speed[0] += 1
				# Adjust angle based on where it hits the left paddle
				relative_position = (self.ball_coordinates.y - (self.left_paddle_coordinates.y -self.paddle_height)) / (self.paddle_height * 2)
				self.ball_speed[1] = ((relative_position - 0.5) * 2) * abs(self.ball_speed[0]) # y speed
			else:
				# right wins point
				# print("RIGHT POINT")
				self.even_odd_ball_direction += 1
				self.even_odd_ball_direction = self.even_odd_ball_direction % 2
				self.right_score += 1
				self.reset_game_position()

	def too_far_right(self):
		# too far right
		if (self.ball_coordinates.x + self.ball_coordinates.width >= self.right_paddle_coordinates.x - self.paddle_width):
			# hit right paddle
			if (self.ball_coordinates.y >= self.right_paddle_coordinates.y - self.paddle_height
				and self.ball_coordinates.y <= self.right_paddle_coordinates.y + self.paddle_height):
				self.ball_speed[0] = -abs(self.ball_speed[0]) # x speed
				self.ball_speed[0] -= 1
				# Adjust angle based on where it hits the right paddle
				relative_position = (self.ball_coordinates.y - (self.right_paddle_coordinates.y - self.paddle_height)) / (self.paddle_height * 2)
				self.ball_speed[1] = ((relative_position - 0.5) * 2) * abs(self.ball_speed[0]) # y speed
			else:
				# left wins point
				# print("LEFT POINT")
				self.even_odd_ball_direction += 1
				self.even_odd_ball_direction = self.even_odd_ball_direction % 2
				self.left_score += 1
				self.reset_game_position()

	def ball_check_x_coord(self):
		self.too_far_left()
		self.too_far_right()
		self.check_and_set_if_ball_over_speed_limit()

	def ball_check_y_coord(self):
		# hit top wall
		if self.ball_speed[1] < 0 and self.ball_coordinates.y - self.ball_coordinates.height <= 0:
			self.ball_speed[1] *= -1
		# hit bottom wall
		if self.ball_speed[1] > 0 and self.ball_coordinates.y + self.ball_coordinates.height >= self.screen_height:
			self.ball_speed[1] *= -1

	def ball_checks(self):
		self.ball_check_x_coord()
		self.ball_check_y_coord()

	def move_ball_left(self):
		if self.ball_speed[0] < 0:
			self.ball_coordinates.x += self.ball_speed[0]

	def move_ball_right(self):
		if self.ball_speed[0] > 0:
			self.ball_coordinates.x += self.ball_speed[0]

	def move_ball_up(self):
		if self.ball_speed[1] < 0:
			self.ball_coordinates.y += self.ball_speed[1]

	def move_ball_down(self):
		if self.ball_speed[1] > 0:
			self.ball_coordinates.y += self.ball_speed[1]

	def check_and_set_if_ball_over_speed_limit(self):
		# x
		if self.ball_speed[0] > self.ball_speed_limit:
			self.ball_speed[0] = self.ball_speed_limit
		if self.ball_speed[0] < -self.ball_speed_limit:
			self.ball_speed[0] = -self.ball_speed_limit
		# y
		if self.ball_speed[1] > self.ball_speed_limit:
			self.ball_speed[1] = self.ball_speed_limit
		if self.ball_speed[1] < -self.ball_speed_limit:
			self.ball_speed[1] = -self.ball_speed_limit

	def move_ball(self):
		self.move_ball_left()
		self.move_ball_right()
		self.move_ball_up()
		self.move_ball_down()
		self.ball_checks()

	def set_ball_initial_coordinates_to_ball_coordinates(self):
		self.ball_coordinates.x = self.ball_initial_coordinates.x
		self.ball_coordinates.y = self.ball_initial_coordinates.y	 
		self.ball_coordinates.width = self.ball_initial_coordinates.width
		self.ball_coordinates.height = self.ball_initial_coordinates.height

	def set_left_paddle_initial_coordinates_to_left_paddle_coordinates(self):
		self.left_paddle_coordinates.x = self.left_paddle_initial_coordinates.x
		self.left_paddle_coordinates.y = self.left_paddle_initial_coordinates.y	 
		self.left_paddle_coordinates.width = self.left_paddle_initial_coordinates.width
		self.left_paddle_coordinates.height = self.left_paddle_initial_coordinates.height

	def set_right_paddle_initial_coordinates_to_right_paddle_coordinates(self):
		self.right_paddle_coordinates.x = self.right_paddle_initial_coordinates.x
		self.right_paddle_coordinates.y = self.right_paddle_initial_coordinates.y	 
		self.right_paddle_coordinates.width = self.right_paddle_initial_coordinates.width
		self.right_paddle_coordinates.height = self.right_paddle_initial_coordinates.height

	def create_ball_paddles_scoreboard(self):
		# ball
		self.set_ball_initial_coordinates_to_ball_coordinates()
		# left paddle
		self.set_left_paddle_initial_coordinates_to_left_paddle_coordinates()
		# right paddle
		self.set_right_paddle_initial_coordinates_to_right_paddle_coordinates()

	def reset_ball_speed(self):
		direction = ((-1) ** self.even_odd_ball_direction) * self.initial_direction
		self.ball_starting_speed = [7 * direction, 0]
		self.ball_speed = [self.ball_starting_speed[0], self.ball_starting_speed[1]]

	def reset_game_position(self):
		# ball
		self.set_ball_initial_coordinates_to_ball_coordinates()
		# left paddle
		self.set_left_paddle_initial_coordinates_to_left_paddle_coordinates()
		# right paddle
		self.set_right_paddle_initial_coordinates_to_right_paddle_coordinates()
		# ball speed
		self.reset_ball_speed()
		# reset pressed key
		self.w_pressed = 0
		self.s_pressed = 0
		self.up_pressed = 0
		self.down_pressed = 0
		# print new scores
		# Game end condition the stop the game
		if (self.left_score or self.right_score) >= self.game_end_condition:
			self.game_running = 0
			self.winner = "left player"
			if self.right_score > self.left_score:
				self.winner = "right player"
			# remember to add call to sheris api and notify that game has ended

	def is_game_running(self):
		return self.game_running

	def set_game_running(self, running_or_not):
		self.game_running = running_or_not

	def return_game_state(self):
		# self.screen_width: int = 1920 # x
		# self.screen_height: int = 1080 # y
		ball_world_pos_x = self.ball_coordinates.x / self.screen_width
		ball_world_pos_y = self.ball_coordinates.y / self.screen_height
		left_paddle_world_pos_x = self.left_paddle_coordinates.x / self.screen_width
		left_paddle_world_pos_y = self.left_paddle_coordinates.y / self.screen_height
		right_paddle_world_pos_x = self.right_paddle_coordinates.x / self.screen_width
		right_paddle_world_pos_y = self.right_paddle_coordinates.y / self.screen_height
		state = str(ball_world_pos_x)
		state += ','
		state += str(ball_world_pos_y)
		state += ','
		state += str(left_paddle_world_pos_x)
		state += ','
		state += str(left_paddle_world_pos_y)
		state += ','
		state += str(right_paddle_world_pos_x)
		state += ','
		state += str(right_paddle_world_pos_y)
		state += ','
		state += str(self.left_score)
		state += ','
		state += str(self.right_score)
		state += ','
		state += str(self.game_running)
		return state

	def left_paddle_pressed_up(self):
		self.w_pressed = 1

	def left_paddle_released_up(self):
		self.w_pressed = 0

	def left_paddle_pressed_down(self):
		self.s_pressed = 1

	def left_paddle_released_down(self):
		self.s_pressed = 0

	def right_paddle_pressed_up(self):
		self.up_pressed = 1

	def right_paddle_released_up(self):
		self.up_pressed = 0

	def right_paddle_pressed_down(self):
		self.down_pressed = 1

	def right_paddle_released_down(self):
		self.down_pressed = 0

games_lock = threading.Lock()
with games_lock:
	games = [0,1,2,3]
	games[0] = Game()
	games[1] = Game()
	games[2] = Game()
	games[3] = Game()

thread = None
thread_lock = threading.Lock()
with thread_lock:
	background_thread_running = 0

def game_loop():
	# this is backgroung thread that is lurking in the background
	# it needs to be started before setting up games
	# yes it needs to be running even when games are not running
	# so it will be ready when game start
	global background_thread_running
	global games_lock
	global games
	global socketio
	while True:
		if background_thread_running == 0:
			return
		with games_lock:
			for game in range(4):
				if games[game].is_game_running() == 1:
					games[game].move_paddles()
					games[game].move_ball()
					socketio.emit('state', games[game].return_game_state())

		time.sleep(0.02)

def start_background_loop(splitted_command):
	global thread
	global thread_lock
	global socketio
	global background_thread_running
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	with thread_lock:
		if thread:
			socketio.emit('message', 'ERROR, background loop already running.')
			return
		else:
			background_thread_running = 1
			thread = threading.Thread(target=game_loop)
			thread.start()
			socketio.emit('message', 'OK: background loop started.')
			return

def stop_background_loop(splitted_command):
	global thread
	global thread_lock
	global background_thread_running
	global socketio
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	with thread_lock:
		if background_thread_running == 0:
			socketio.emit('message', 'ERROR, game loop already stopped.')
			return
		else:
			background_thread_running = 0
			thread = None
			socketio.emit('message', 'OK, gameloop stopped.')
			return

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
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 1:
			socketio.emit('message', 'ERROR, game already running cannot create new.')
			return
		else:
			games[number].set_game_running(1)
			games[number].new_game_initilization()
			games[number].set_game_slot(number)
			socketio.emit('message', 'OK, game running {}.'.format(number))
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
			state = games[number].return_game_state()
			socketio.emit('message', 'OK, ' + str(state) + '.')
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
			if games[index].game_running == 1:
				games_running[index] = '1'
	socketio.emit('message', 'OK, {}'.format(str(','.join(games_running))))
	return

def left_paddle_up(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].left_paddle_pressed_up()
			socketio.emit('message', 'OK, left paddle pressed up.')
			return

def left_paddle_down(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].left_paddle_pressed_down()
			socketio.emit('message', 'OK, left paddle pressed down.')
			return

def left_paddle_down_release(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR: allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].left_paddle_released_down()
			socketio.emit('message', 'OK, left paddle released down.')
			return

def left_paddle_up_release(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].left_paddle_released_up()
			socketio.emit('message', 'OK, left paddle released up.')
			return

def right_paddle_up(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].right_paddle_pressed_up()
			socketio.emit('message', 'OK, right paddle pressed up.')
			return

def right_paddle_down(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].right_paddle_pressed_down()
			socketio.emit('message', 'OK, right paddle pressed down.')
			return

def right_paddle_down_release(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].right_paddle_released_down()
			socketio.emit('message', 'OK, right paddle released down.')
			return

def right_paddle_up_release(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 2:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	number = int(splitted_command[1])
	if number < 0 or number > 3:
		socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
		return
	with games_lock:
		if games[number].is_game_running() == 0:
			socketio.emit('message', 'ERROR, game not running so no keypresses.')
			return
		else:
			games[number].right_paddle_released_up()
			socketio.emit('message', 'OK, right paddle released up.')
			return

#@app.route('/')
#def index():
#    return render_template('index.html')

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
	#print('Message:', message)
	global socketio
	socketio.emit('message', 'Server received your message: ' + message)
	splitted_command = message.split(",")
	if splitted_command:
		match splitted_command[0]:
			case 'start_background_loop':
				start_background_loop(splitted_command)
			case 'stop_background_loop':
				stop_background_loop(splitted_command)
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
			case 'left_paddle_up':
				left_paddle_up(splitted_command)
			case 'left_paddle_down':
				left_paddle_down(splitted_command)
			case 'left_paddle_down_release':
				left_paddle_down_release(splitted_command)
			case 'left_paddle_up_release':
				left_paddle_up_release(splitted_command)
			case 'right_paddle_up':
				right_paddle_up(splitted_command)
			case 'right_paddle_down':
				right_paddle_down(splitted_command)
			case 'right_paddle_down_release':
				right_paddle_down_release(splitted_command)
			case 'right_paddle_up_release':
				right_paddle_up_release(splitted_command)
			case _:
				socketio.emit('message', 'ERROR, command not recognised: ' + message)
	else:
		socketio.emit('message', 'ERROR, nothing was sent.')

if __name__ == '__main__':
	# Use SSL/TLS encryption for WSS
	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ssl_context.load_cert_chain('/server.crt', '/server.key')
	socketio.run(app, host='0.0.0.0', port=8888, debug=True, ssl_context=ssl_context, allow_unsafe_werkzeug=True)
	#socketio.run(app, host='0.0.0.0', port=8888, debug=True, allow_unsafe_werkzeug=True)
