import threading

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
