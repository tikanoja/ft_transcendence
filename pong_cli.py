import socketio
import sys
import time

class colors:
    HEADER = '\033[96m'
    OKBLUE = '\033[94m'
    OKPINK = '\033[95m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text, color):
    print(color + text + colors.ENDC)

# Define event handlers
def on_connect():
    print('Connected to server')


def on_games_running_response(data):
    print('Games running response:', data)
    valuesArray = data.split(',')
    print(valuesArray)
    index = 0
    while index != 4:
        index += 1
        if valuesArray[index] != '0' and valuesArray[index] != ' 0':
            print(index)
            print_color(str(index - 1), colors.HEADER)
    if interactive_mode == False:
        sio.disconnect()


def watch_game(game_number):
    last_print_time = [time.time()]  # Mutable list to store last print time
    sio.on('state', lambda data: on_state(data, last_print_time))
    # while not stop_flag[0]:
    #     time.sleep(1)

def on_state(data, last_print_time):
    current_time = time.time()
    if current_time - last_print_time[0] >= 2:
        print('Game State:', data)
        last_print_time[0] = current_time  # Update last print time

def on_disconnect():
    print('Disconnected from server')

def on_message(data):
    print('Message from server:', data)
    if interactive_mode == False:
        sio.disconnect()

def print_commands():
    header = colors.HEADER + colors.BOLD + colors.UNDERLINE + "\n\t\t\tAvailable Commands" + colors.HEADER + colors.ENDC
    games_running = colors.HEADER + "\n\ngames_running:" + colors.ENDC + "\tshows all currently running games"
    watch_game = colors.HEADER + "\n\nwatch_game,<game number>:" + colors.ENDC + "\tshows the current score of the chosen game"
    print(header + games_running + "\n" + watch_game + "\n\n")

def print_help():
    header = colors.HEADER + colors.BOLD + colors.UNDERLINE + "\n\t\t\tPong CLI Usage" + colors.HEADER + colors.ENDC
    usage = colors.HEADER + "Usage:" + colors.ENDC + "  pong_cli.py [-h] [-i] <command>" + colors.ENDC
    available_commands = colors.HEADER + """\n\nAvailable commands:""" + colors.ENDC 
    options = colors.HEADER + "\n\nOptions:" + colors.ENDC + "\n\t-h, --help show this help message and exit \n\t-i, --interactive  Interactive mode"
    help_message = header + "\n\n" + usage + available_commands + options
    print(help_message)


if __name__ == "__main__":

    interactive_mode = False

    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit()

    if '-i' in sys.argv or '--interactive' in sys.argv:
        interactive_mode = True

    sio = socketio.Client(ssl_verify=False)
    server_url = 'wss://localhost:8888'  # Your server URL
    sio.connect(server_url)

    # Register event handlers
    sio.on('connect', on_connect)
    sio.on('message', on_message)
    sio.on('games_running_response', on_games_running_response)
    sio.on('disconnect', on_disconnect)

    if interactive_mode == False:
        sio.emit('message', sys.argv[1])
        sio.wait()
    else:
        print_commands()
        while True:
            try:
                command = input("Enter command (type 'exit' to quit): ")
                if command.lower() == 'exit':
                    break
                # if command == 'watch_game,0':
                #     game_number = 0
                #     watch_game(game_number)
                sio.emit('message', command)
            except KeyboardInterrupt:
                break
    sio.disconnect()
