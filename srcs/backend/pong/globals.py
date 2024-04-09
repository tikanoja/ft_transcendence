import threading
from flask import Flask
from flask_socketio import SocketIO
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

# own class that holds all game data
import Game

games_lock = threading.Lock()
games = [0,1,2,3]
games[0] = Game.Game()
games[1] = Game.Game()
games[2] = Game.Game()
games[3] = Game.Game()

thread = None
thread_lock = threading.Lock()
background_thread_running = 0
