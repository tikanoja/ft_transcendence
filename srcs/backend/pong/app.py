import time
import threading
import ssl
import random
import requests
from typing import Optional
from dataclasses import dataclass
from flask import Flask, request, jsonify # ,current_app is this needed?
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_restful import Resource, Api

app = Flask(__name__)

CORS(app)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
		self.ball_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
		self.ball_initial_coordinates: Optional[GameObject.GameObject] = None # x,y,width,height
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
		self.game_end_condition: int = 1 # how many points till end
		self.game_running: int = 0 # 1 running, 0 end
		self.winner: str = 'nobody'
		self.left_player_id: str = 'left_player'
		self.right_player_id: str = 'right_player'
		self.create_ball_initial_coordinates()
		self.create_left_paddle_initial_coordinates()
		self.create_right_paddle_initial_coordinates()
		self.ball_bounces: int = 0

	def set_game_slot(self, number):
		self.game_slot = number

	def clear_scores(self):
		self.left_score = 0
		self.right_score = 0

	def new_game_initilization(self):
		self.clear_scores()
		self.initialize_ball_and_paddles()
		self.w_pressed = 0
		self.s_pressed = 0
		self.up_pressed = 0
		self.down_pressed = 0
		self.ball_bounces = 0

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

	def too_far_left(self): # checks if ball hits left paddle
		if (self.ball_coordinates.x - self.ball_coordinates.width <= self.left_paddle_coordinates.x + self.paddle_width):
			# if hit left paddle
			if (self.ball_coordinates.y >= self.left_paddle_coordinates.y - self.paddle_height
				and self.ball_coordinates.y <= self.left_paddle_coordinates.y + self.paddle_height):
				self.ball_speed[0] = abs(self.ball_speed[0]) # reverse x speed
				self.ball_speed[0] += 1 # increase ball speed
				self.ball_bounces += 1 # incease how many times the ball has bounced
				# Adjust angle based on where it hits the left paddle
				relative_position = (self.ball_coordinates.y - (self.left_paddle_coordinates.y -self.paddle_height)) / (self.paddle_height * 2)
				self.ball_speed[1] = ((relative_position - 0.5) * 2) * abs(self.ball_speed[0]) # y speed depends where it hit on the paddle
			else: # went past left paddle
				# right wins point
				self.even_odd_ball_direction += 1                               # change ball starting direction
				self.even_odd_ball_direction = self.even_odd_ball_direction % 2 # if more than 1 set to 0
				self.right_score += 1 # increase score
				self.reset_game_position() # also checks has the game ended


	def too_far_right(self): # checks if ball hits right paddle
		if (self.ball_coordinates.x + self.ball_coordinates.width >= self.right_paddle_coordinates.x - self.paddle_width):
			# if hit right paddle
			if (self.ball_coordinates.y >= self.right_paddle_coordinates.y - self.paddle_height
				and self.ball_coordinates.y <= self.right_paddle_coordinates.y + self.paddle_height):
				self.ball_speed[0] = -abs(self.ball_speed[0]) # reverse x speed
				self.ball_speed[0] -= 1 # increase ball speed
				self.ball_bounces += 1 # incease how many times the ball has bounced
				# Adjust angle based on where it hits the right paddle
				relative_position = (self.ball_coordinates.y - (self.right_paddle_coordinates.y - self.paddle_height)) / (self.paddle_height * 2)
				self.ball_speed[1] = ((relative_position - 0.5) * 2) * abs(self.ball_speed[0]) # y speed depends where it hit on the paddle
			else:
				# left wins point
				self.even_odd_ball_direction += 1                               # change ball starting direction
				self.even_odd_ball_direction = self.even_odd_ball_direction % 2 # if more than 1 set to 0
				self.left_score += 1 # increase score
				self.reset_game_position() # also checks has the game ended

	def ball_check_x_coord(self): # has the ball hit anything in x direction
		self.too_far_left() # did it hit left paddle
		self.too_far_right() # did it hit right paddle
		self.check_and_set_if_ball_over_speed_limit() # if ball speed too fast then cap the speed

	def ball_check_y_coord(self): # has the ball hit anything in y direction
		# hit top wall
		if self.ball_speed[1] < 0 and self.ball_coordinates.y - self.ball_coordinates.height <= 0:
			self.ball_speed[1] *= -1 # reverse y speed
		# hit bottom wall
		if self.ball_speed[1] > 0 and self.ball_coordinates.y + self.ball_coordinates.height >= self.screen_height:
			self.ball_speed[1] *= -1 # reverse y speed

	def ball_checks(self): # has the ball hit anything
		self.ball_check_x_coord() # x checks
		self.ball_check_y_coord() # y checks

	def move_ball_left(self): # moves the ball
		if self.ball_speed[0] < 0:
			self.ball_coordinates.x += self.ball_speed[0]

	def move_ball_right(self): # moves the ball
		if self.ball_speed[0] > 0:
			self.ball_coordinates.x += self.ball_speed[0]

	def move_ball_up(self): # moves the ball
		if self.ball_speed[1] < 0:
			self.ball_coordinates.y += self.ball_speed[1]

	def move_ball_down(self): # moves the ball
		if self.ball_speed[1] > 0:
			self.ball_coordinates.y += self.ball_speed[1]

	def check_and_set_if_ball_over_speed_limit(self): # cap the ball speed
		# x direction
		if self.ball_speed[0] > self.ball_speed_limit:
			self.ball_speed[0] = self.ball_speed_limit
		if self.ball_speed[0] < -self.ball_speed_limit:
			self.ball_speed[0] = -self.ball_speed_limit
		# y direction
		if self.ball_speed[1] > self.ball_speed_limit:
			self.ball_speed[1] = self.ball_speed_limit
		if self.ball_speed[1] < -self.ball_speed_limit:
			self.ball_speed[1] = -self.ball_speed_limit

	def move_ball(self): # move ball and do hit checks
		self.move_ball_left()
		self.move_ball_right()
		self.move_ball_up()
		self.move_ball_down()
		self.ball_checks()

	def set_ball_initial_coordinates_to_ball_coordinates(self): # initializes ball coordinates
		self.ball_coordinates.x = self.ball_initial_coordinates.x
		self.ball_coordinates.y = self.ball_initial_coordinates.y	 
		self.ball_coordinates.width = self.ball_initial_coordinates.width
		self.ball_coordinates.height = self.ball_initial_coordinates.height

	def set_left_paddle_initial_coordinates_to_left_paddle_coordinates(self): # initializes left paddle coordinates
		self.left_paddle_coordinates.x = self.left_paddle_initial_coordinates.x
		self.left_paddle_coordinates.y = self.left_paddle_initial_coordinates.y	 
		self.left_paddle_coordinates.width = self.left_paddle_initial_coordinates.width
		self.left_paddle_coordinates.height = self.left_paddle_initial_coordinates.height

	def set_right_paddle_initial_coordinates_to_right_paddle_coordinates(self): # initialize right paddle coordinates
		self.right_paddle_coordinates.x = self.right_paddle_initial_coordinates.x
		self.right_paddle_coordinates.y = self.right_paddle_initial_coordinates.y	 
		self.right_paddle_coordinates.width = self.right_paddle_initial_coordinates.width
		self.right_paddle_coordinates.height = self.right_paddle_initial_coordinates.height

	def initialize_ball_and_paddles(self): # initialize coordinates of ball and paddles
		# ball
		self.set_ball_initial_coordinates_to_ball_coordinates()
		# left paddle
		self.set_left_paddle_initial_coordinates_to_left_paddle_coordinates()
		# right paddle
		self.set_right_paddle_initial_coordinates_to_right_paddle_coordinates()

	def reset_ball_speed(self): # initialize ball speed to starting slow speed
		direction = ((-1) ** self.even_odd_ball_direction) * self.initial_direction
		self.ball_starting_speed = [7 * direction, 0]
		self.ball_speed = [self.ball_starting_speed[0], self.ball_starting_speed[1]]

	def reset_game_position(self): # resets the game position to beginning and also checks if the game has ended
		# ball
		self.set_ball_initial_coordinates_to_ball_coordinates()
		# left paddle
		self.set_left_paddle_initial_coordinates_to_left_paddle_coordinates()
		# right paddle
		self.set_right_paddle_initial_coordinates_to_right_paddle_coordinates()
		# ball speed
		self.reset_ball_speed()
		# reset pressed keys
		self.w_pressed = 0
		self.s_pressed = 0
		self.up_pressed = 0
		self.down_pressed = 0
		# print new scores
		# Check game end condition the stop the game if necessary
		if (self.left_score or self.right_score) >= self.game_end_condition:
			self.game_running = 0 # set game not running
			self.winner = self.left_player_id
			if self.right_score > self.left_score:
				self.winner = self.right_player_id
			socketio.emit('endstate', games[self.game_slot].return_game_state())
			send_game_over_data(self.right_score, self.left_score, self.ball_bounces)
			self.game_slot = -1
			self.ball_bounces = 0

	def is_game_running(self): # returns the state of game is it running
		return self.game_running

	def set_game_running(self, running_or_not): # sets game state so it is running
		self.game_running = running_or_not

	def return_game_state(self): # returns all necessary information of game state to frontend to render
		# self.screen_width: int = 1920 # x
		# self.screen_height: int = 1080 # y
		ball_world_pos_x = self.ball_coordinates.x / self.screen_width # calculates relative position between 0 and 1
		ball_world_pos_y = self.ball_coordinates.y / self.screen_height # calculates relative position between 0 and 1
		left_paddle_world_pos_x = self.left_paddle_coordinates.x / self.screen_width # calculates relative position between 0 and 1
		left_paddle_world_pos_y = self.left_paddle_coordinates.y / self.screen_height # calculates relative position between 0 and 1
		right_paddle_world_pos_x = self.right_paddle_coordinates.x / self.screen_width # calculates relative position between 0 and 1
		right_paddle_world_pos_y = self.right_paddle_coordinates.y / self.screen_height # calculates relative position between 0 and 1
		state = str(self.game_slot) # game was in which slot 
		state += ','
		state += str(ball_world_pos_x) # ball x position
		state += ','
		state += str(ball_world_pos_y) # ball y position
		state += ','
		state += str(left_paddle_world_pos_x) # left paddle x position
		state += ','
		state += str(left_paddle_world_pos_y) # left paddle y position
		state += ','
		state += str(right_paddle_world_pos_x) # left paddle x position
		state += ','
		state += str(right_paddle_world_pos_y) # left paddle y position
		state += ','
		state += str(self.left_score) # left player score
		state += ','
		state += str(self.right_score) # right player score
		state += ','
		state += str(self.game_running) # is game running
		state += ','
		state += str(self.ball_bounces) # how  many times the ball have bounced to paddles
		return state

	def left_paddle_pressed_up(self): # left paddle up pressed
		self.w_pressed = 1

	def left_paddle_released_up(self): # left paddle up released
		self.w_pressed = 0

	def left_paddle_pressed_down(self): # left paddle pressed down
		self.s_pressed = 1

	def left_paddle_released_down(self): # left paddle down released
		self.s_pressed = 0

	def right_paddle_pressed_up(self): # right paddle pressed up
		self.up_pressed = 1

	def right_paddle_released_up(self): # right paddle up released
		self.up_pressed = 0

	def right_paddle_pressed_down(self): # right paddle down pressed
		self.down_pressed = 1

	def right_paddle_released_down(self): # right paddle down released
		self.down_pressed = 0

games_lock = threading.Lock() # creating mutex lock for games so only one thing can access game data at one time
with games_lock: # lock the mutex lock, will be release automatically when the 5 lines below are executed
	games = [0,1,2,3] # create room for 4 games
	games[0] = Game() # create Game 0
	games[1] = Game() # create Game 1
	games[2] = Game() # create Game 2
	games[3] = Game() # create Game 3

thread = None # c style null pointer to thread, will be started later
thread_lock = threading.Lock() # crete mutex lock for thread so only one thing  at a time can set up background thread
with thread_lock: # lock the mutex lock, will be released automatically when the 1 line below is executed
	background_thread_running = 0 # set value for 0 to mark up that background thread is not running

def game_loop():
	global background_thread_running
	global games_lock
	global games
	global socketio
	while True:
		if background_thread_running == 0: # return if background thread has no permission to run
			return
		with games_lock: # lock the mutex lock and update games that are running
			for game in range(4):
				if games[game].is_game_running() == 1:
					games[game].move_paddles()
					games[game].move_ball()
					socketio.emit('state', games[game].return_game_state())
		time.sleep(0.02) # 50 times per second

# string format is "set_game_settings,0,player1,player2" 
def set_game_settings(splitted_command):
	global socketio
	global games
	global games_lock
	if len(splitted_command) != 4:
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
			# DONT FORGET in here we should insert the check if django approves game start
			games[number].left_player_id = splitted_command[2]
			games[number].right_player_id = splitted_command[3]
			socketio.emit('message', 'OK, game settings set.')
			return

# returns "OK, 0,0,1,0" if there is only 1 game running and it is on slot 2
def	games_running(splitted_command):
	global games
	global games_lock
	if len(splitted_command) != 1:
		socketio.emit('message', 'ERROR, string not in right format.')
		return
	games_running = ['0','0','0','0'] # initialize to 0
	with games_lock:
		for index in range(4):
			if games[index].game_running == 1:
				games_running[index] = '1'
	socketio.emit('games_running_response', 'OK, {}'.format(str(','.join(games_running))))
	return

# start game on specific slot
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
	with games_lock:
		if games[number].is_game_running() == 1:
			socketio.emit('message', 'ERROR, game already running cannot create new.')
			return
		else:
			games[number].new_game_initilization()
			games[number].set_game_slot(number)
			games[number].set_game_running(1)
			socketio.emit('start_game', 'OK,{}'.format(number))
			return

	# LET THIS STAY here commented out for know, remove only after timo and sheree have checked that everything works as should
	#with games_lock:
	#    for index in range(4):
	#        if games[index].game_running == 0:
	#            number = index
	#            break
	#with games_lock:
	#    if number == -1:
	#        socketio.emit('message', 'ERROR, game already running cannot create new.')
	#        return
	#    else:
	#        games[number].new_game_initilization()
	#        games[number].set_game_slot(number)
	#        games[number].set_game_running(1)
	#        socketio.emit('start_game', 'OK,{}'.format(number))
	#        return

# stops game from specific slot
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

# get state of game from specific slot
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

# sets left paddle has been pressed up
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

# sets left paddle has been pressed down
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

# sets that left paddle down has been released
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

# sets left paddle up has been released 
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
			return

# right paddle up has been pressed
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
			return

# right paddle has been pressed down
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

# right paddle down has been released
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

# right paddle up has been released
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
			socketio.emit('message', 'OK, right paddle released up.')
			games[number].right_paddle_released_up()
			return

# when the connection has been established
@socketio.on('connect')
def handle_connect():
	global socketio
	socketio.emit('message', 'client connected')

# when the connection has been disconnected 
@socketio.on('disconnect')
def handle_disconnect():
	pass

# DONT FORGET is this function actually needed?
def get_state_cli(splitted_command):
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
			socketio.emit('state_cli', games[number].return_game_state())
			return

# server gets message event and handles it accordingly
@socketio.on('message')
def handle_message(message):
	global socketio
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
			case 'get_state_cli':
				get_state_cli(splitted_command)
			case _:
				socketio.emit('message', 'ERROR, command not recognised: ' + message)
	else:
		socketio.emit('message', 'ERROR, nothing was sent.')


@socketio.on('username')
def validate_username(data):
	global games
	global games_lock
	global socketio
	usernames = data.split(",")
	data_to_send = { "p1_username": usernames[0],
	"p2_username": usernames[1]
	}

	with app.app_context():
		django_url = "http://transcendence:8000/pong/validate_match/"
		try:

			slot = -1
			response = requests.post(django_url, data=data_to_send)
			if response.status_code == 200:
				with games_lock:
					for index in range(4):
						if games[index].is_game_running() == 0:
							slot = index
							break
					if slot == -1:
						return jsonify({"message": "ERROR, all game slots are already in use"})
					else:
						games[slot].left_player_id = usernames[1]
						games[slot].right_player_id = usernames[0]
						print("Emiting setup game")
						socketio.emit('setup_game', 'OK,{}'.format(slot))
						return jsonify({"message": "Usernames verified"})
			else:
				return jsonify({"error": "Failed to send request"}), response.status_code
		except Exception as e:
			print("threw except", str(e))
			return jsonify({"error": str(e)}), 500

# @app.route('/send_game_over_data', methods=['POST'])
def send_game_over_data(p1_score, p2_score, rally):
	data_to_send = {"game" : "Pong",
		"p1_username": "hen",
		"p1_score": f"{p1_score}",
		"p2_username": "jen",
		"p2_score": f"{p2_score}",
		"longest_rally": f"{rally}"
	}
	with app.app_context():
		django_url = "http://transcendence:8000/pong/send_game_data/"

		try:
			response = requests.post(django_url, data=data_to_send)
			print('Response from sending game data: ', response)
			if response.status_code == 200:
				return jsonify({"message": "Request sent successfully"})
			else:
				return jsonify({"error": "Failed to send request"}), response.status_code
		except Exception as e:
			print("threw except", str(e))
			return jsonify({"error": str(e)}), 500


@app.route('/init_usernames', methods=['GET'])
def init_usernames():
	try:
		print("inside try")
		# Assuming the request body contains JSON data with 'p1_username' and 'p2_username'
		data = request.get_json()
		p1_username = data['p1_username']
		p2_username = data['p2_username']
		# Process the data as needed
		# For example, you can return a response indicating success
		return jsonify({'message': 'Usernames initialized successfully', 'p1_username': p1_username, 'p2_username': p2_username}), 200
	except Exception as e:
		# Handle any errors
		return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
	# Use SSL/TLS encryption for WSS
	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ssl_context.load_cert_chain('/server.crt', '/server.key')
	with thread_lock:
		background_thread_running = 1
		thread = threading.Thread(target=game_loop)
		thread.start()
	socketio.run(app, host='0.0.0.0', port=8888, debug=True, ssl_context=ssl_context, allow_unsafe_werkzeug=True)
