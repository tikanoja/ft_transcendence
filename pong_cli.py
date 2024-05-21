import socketio
import socketio.client
import json
import sys
import time
import os
import select
import requests
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
    watch_game = colors.HEADER + "\n\nwatch_game:" + colors.ENDC + "\tshows the current score of the chosen game"
    dashboard = colors.HEADER + "\n\ndashboard: " + colors.ENDC + "\tshows the current pong stats for the given user"
    print(header + games_running + "\n" + watch_game + dashboard  + "\n\n")


def print_help():
    header = colors.HEADER + colors.BOLD + "\n\t\t" + colors.UNDERLINE + "Pong CLI Usage" + colors.HEADER + colors.ENDC
    usage = colors.HEADER + "Usage:" + colors.ENDC + "  pong_cli.py [-h] [-i] <command>" + colors.ENDC
    print_commands()
    options = colors.HEADER + "\n\nOptions:" + colors.ENDC + "\n\t-h, --help show this help message and exit \n\t-i, --interactive  Interactive mode"
    help_message = header + "\n\n" + usage + options
    print(help_message)

def on_connect():
    print('Connected to server')

def on_games_running_response(data):
    sio.on('message', print_message)
    valuesArray = data.split(',')
    index = 0
    while index != 4:
        index += 1
        if valuesArray[index] != '0' and valuesArray[index] != ' 0':
            print_color(str(index - 1), colors.HEADER)
    if interactive_mode == False:
        sio.disconnect()

game_over = False

def end_game(data, game_number):
    global game_over
    print_state(data, game_number)
    game_over = True

def print_message(data):
    if (data == "ERROR, game not running so no state."):
        print(data + "press enter to exit, or wait for a game to start")
    else:
        print(data)

def watch_game(game_number):
    global game_over
    os.system('clear')
    sio.on('state_cli', lambda data: print_state(data, game_number))
    sio.on('message', print_message)
    sio.on('endstate', lambda data: end_game(data, game_number))
    try:
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or game_over:
                if(game_over):
                    print_color("game over", colors.OKGREEN)
                game_over = False
                print(colors.WARNING + "Exiting watch_game, press enter......" + colors.ENDC)
                _ = sys.stdin.readline()
                break
            sio.emit('message', 'get_state_cli,' + game_number)
            time.sleep(5)
    except KeyboardInterrupt:
        print(colors.WARNING + "Keyboard interrupt detected. Exiting watch_game......" + colors.ENDC)


def print_state(data, game_number):
    valuesArray = data.split(',')
    global game_over
    os.system('clear')
    print_banner()
    print(colors.HEADER + colors.BOLD + "\nWatching game: " + game_number + " Press enter to exit.\n\n" + colors.ENDC)
    print(colors.HEADER + colors.BOLD + "P1 score:   " + colors.ENDC)
    print(valuesArray[7])
    print(colors.HEADER + colors.BOLD + "P2 score:   " + colors.ENDC)
    print(valuesArray[8])
    print(colors.HEADER + colors.BOLD + "Longest Rally:   " + colors.ENDC)
    print(valuesArray[10])


def print_dashboard(username, data):
    games_played = data['pong']['games_played']
    wins = data['pong']['wins']
    win_percentage = (wins / games_played) * 100 if games_played != 0 else 0
    print(colors.HEADER + colors.BOLD + colors.UNDERLINE + "\nUser Stats for " + username + colors.ENDC + "\n\n")
    print(colors.HEADER + colors.BOLD + "Games Played:  " + colors.ENDC + str(games_played) + "\n")
    print(colors.HEADER + colors.BOLD + "Wins:  " + colors.ENDC + str(wins) + "\n")
    print(colors.HEADER + colors.BOLD + "Win percentage:  " + colors.ENDC + "{:.2f}%".format(win_percentage) + "\n")



def send_get_dashboard_request(username):
    url = f'https://localhost/pong/cli_dashboard/{username}'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        try:
            data = response.json()
            print_dashboard(username, data)
        except ValueError:
            print("Empty or non-JSON response")
    else:
        print("Error:", response.status_code)



def on_disconnect():
    print('Disconnected from server')

def run_command(argv):
    if argv[1] == "games_running":
        sio.emit('message', 'games_running')
        sio.on('games_running_response', on_games_running_response)
        sio.wait()
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
    elif argv[1] == "dashboard":
        username = input("Enter a username: ")
        send_get_dashboard_request(username)
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

    client_name = "CliClient"
    server_url = 'https://localhost:8888'
    sio.connect(server_url)

    sio.on('connect', on_connect)
    sio.on('disconnect', on_disconnect)

    if interactive_mode == False:
        run_command(sys.argv)
        sio.wait()
    else:
        print_banner()
        print_commands()
        while True:
            command = input("Enter command (type 'exit' to quit): ")
            if command.lower() == 'exit':
                break
            if command == 'watch_game':
                game_number = input("Enter a game number: ")
                watch_game(game_number)
            if command == "dashboard":
                username = input("Enter a username: ")
                send_get_dashboard_request(username)
            else:
                sio.emit('message', command)
                run_command(sys.argv)
                sio.on('games_running_response', on_games_running_response)

    sio.disconnect()