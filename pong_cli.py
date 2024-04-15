import argparse
import socketio
import sys
import time

# Define event handlers
def on_connect():
    print('Connected to server')
    sio.emit('message', message)

def on_games_running_response(data):
    print('Games running response:', data)

def watch_game(game_number):
    last_print_time = [time.time()]  # Mutable list to store last print time
    sio.on('state', lambda data: on_state(data, last_print_time))
    while not stop_flag[0]:
        time.sleep(1)

def on_state(data, last_print_time):
    current_time = time.time()
    if current_time - last_print_time[0] >= 2:
        print('Game State:', data)
        last_print_time[0] = current_time  # Update last print time

def on_disconnect():
    print('Disconnected from server')

def on_message(data):
    print('Message from server:', data)
    if not interactive_mode:
        sio.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket.IO Client')
    parser.add_argument('message', type=str, help='Message to send to the server')
    parser.add_argument('--ssl-verify', action='store_true', help='Enable SSL verification')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    message = args.message
    interactive_mode = args.interactive
    stop_flag = [False]

    if args.ssl_verify:
        sio = socketio.Client()
    else:
        sio = socketio.Client(ssl_verify=False)

    # Register event handlers
    sio.on('connect', on_connect)
    sio.on('disconnect', on_disconnect)
    sio.on('games_running_response', on_games_running_response)
    sio.on('message', on_message)

    # Connect to the server
    server_url = 'wss://localhost:8888'  # Your server URL
    sio.connect(server_url)

    if not interactive_mode:
        sio.wait()
    else:
        while True:
            try:
                command = input("Enter command (type 'stop' to quit): ")
                if command.lower() == 'exit':
                    stop_flag[0] = True
                    break
                if interactive_mode and message == 'watch_game,0':
                    game_number = 0
                    watch_game(game_number)
                elif interactive_mode and command.lower() == 'stop':
                    stop_flag[0] = True
                sio.emit('message', command)
            except KeyboardInterrupt:
                break
        sio.disconnect()
