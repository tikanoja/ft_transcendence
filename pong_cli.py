import socketio
import socketio.client
import sys
import time
import select
import warnings
from urllib3.exceptions import InsecureRequestWarning

class colors:
    HEADER = '\033[96m'
    OKGREEN = '\033[92m'
    OKPINK = '\033[95m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def print_color(text, color):
    print(color + text + colors.ENDC)

def print_banner():
    print(colors.OKGREEN + """
    \t██████╗  ██████╗ ███╗   ██╗ ██████╗ 
    \t██╔══██╗██╔═══██╗████╗  ██║██╔════╝ 
    \t██████╔╝██║   ██║██╔██╗ ██║██║  ███╗
    \t██╔═══╝ ██║   ██║██║╚██╗██║██║   ██║
    \t██║     ╚██████╔╝██║ ╚████║╚██████╔╝
    \t╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝    
                                        """ + colors.ENDC)

def print_commands():
    header = colors.HEADER + colors.BOLD + "\n\t\t" + colors.UNDERLINE + "Available Commands" + colors.HEADER + colors.ENDC
    games_running = colors.HEADER + "\n\ngames_running:" + colors.ENDC + "\tshows all currently running games"
    watch_game = colors.HEADER + "\n\nwatch_game,<game number>:" + colors.ENDC + "\tshows the current score of the chosen game"
    print(header + games_running + "\n" + watch_game + "\n\n")

def print_help():
    header = colors.HEADER + colors.BOLD + "\n\t\t" + colors.UNDERLINE + "Pong CLI Usage" + colors.HEADER + colors.ENDC
    usage = colors.HEADER + "Usage:" + colors.ENDC + "  pong_cli.py [-h] [-i] <command>" + colors.ENDC
    available_commands = colors.HEADER + """\n\nAvailable commands:""" + colors.ENDC 
    options = colors.HEADER + "\n\nOptions:" + colors.ENDC + "\n\t-h, --help show this help message and exit \n\t-i, --interactive  Interactive mode"
    help_message = header + "\n\n" + usage + available_commands + options
    print(help_message)

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

game_over = False

def watch_game(game_number):
    global game_over
    sio.on('state_cli', lambda data: print_state(data))
    print(colors.HEADER + colors.BOLD + "Watching game: " + game_number + colors.ENDC)
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or game_over == True:
            game_over = False
            print(colors.WARNING + "Exiting watch_game......" + colors.ENDC)
            _ = sys.stdin.readline()
        sio.emit('message', 'get_state_cli,' + game_number)
        time.sleep(5)

def print_state(data):
    valuesArray = data.split(',')
    global game_over

    index = 0
    while index != 6:
        print(LINE_UP, end=LINE_CLEAR)
        index += 1
    print(colors.HEADER + colors.BOLD + "P1 score:   " + colors.ENDC)
    print(valuesArray[7])
    print(colors.HEADER + colors.BOLD + "P2 score:   " + colors.ENDC)
    print(valuesArray[8])
    print(colors.HEADER + colors.BOLD + "Longest Rally:   " + colors.ENDC)
    print(valuesArray[10])


def on_disconnect():
    print('Disconnected from server')

# def on_message(data):
#     print('Message from server:', data)
#     if interactive_mode == False:
#         sio.disconnect()

#TODO: sabotage MUST be password protected some how

def run_command(argv):
    if argv[1] == "games_running":
        sio .emit('message', 'games_running')
        sio.wait()
        sio.on('games_running_response', on_games_running_response)
    elif argv[1] == "watch_game":
        game_number = input("Enter a game number: ")
        watch_game(game_number)
    elif argv[1] == "sabotage-1 L":
        sio.emit('message', "left_paddle_up,0")
        time.sleep(0.2)
        sio.emit('message', "left_paddle_up_release,0")
    elif argv[1] == "sabotage-12 L":
        sio.emit('message', "left_paddle_down,0")
        time.sleep(0.2)
        sio.emit('message', "left_paddle_release,0")
    elif argv[1] == "sabotage-1 R":
        sio.emit('message', "right_paddle_up,0")
        time.sleep(0.2)
        sio.emit('message', "right_paddle_up_release,0")
    elif argv[1] == "sabotage-12 R":
        sio.emit('message', "right_paddle_down,0")
        time.sleep(0.2)
        sio.emit('message', "right_paddle_release,0")
    else:
        print(colors.WARNING + "not a valid command use -h for help" + colors.ENDC)
    sio.disconnect()

if __name__ == "__main__":

    interactive_mode = False
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) == 1:
        print_banner()
        print_help()
        sys.exit()

    if '-i' in sys.argv or '--interactive' in sys.argv:
        interactive_mode = True

    sio = socketio.Client(ssl_verify=False)
    server_url = 'wss://localhost:8888'  # Your server URL
    sio.connect(server_url)

    sio.on('connect', on_connect)
    sio.on('games_running_response', on_games_running_response)
    sio.on('disconnect', on_disconnect)

    if interactive_mode == False:
        run_command(sys.argv)
        sio.wait()
    else:
        print_banner()
        print_commands()
        while True:
            try:
                command = input("Enter command (type 'exit' to quit): ")
                if command.lower() == 'exit':
                    break
                if command == 'watch_game':
                    game_number = input("Enter a game number: ")
                    watch_game(game_number)
                sio.emit('message', command)
            except KeyboardInterrupt:
                break
    sio.disconnect()
