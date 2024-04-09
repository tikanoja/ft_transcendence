
import globals

def get_state(splitted_command):
    if len(splitted_command) != 2:
        globals.socketio.emit('message', 'ERROR, string not in right format.')
        return
    number = int(splitted_command[1])
    if number < 0 or number > 3:
        globals.socketio.emit('message', 'ERROR, allowed game numbers are 0 to 3.')
        return
    with globals.games_lock:
        if globals.games[number].is_game_running() == 0:
            globals.socketio.emit('message', 'ERROR, game not running so no state.')
            return
        else:
            state = globals.games[number].return_game_state()
            globals.socketio.emit('message', 'OK, ' + str(state) + '.')
            return
