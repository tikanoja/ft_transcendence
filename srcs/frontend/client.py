import socketio
import urllib3 # this will silence the self signed cert warning
# Define event handlers
def on_connect():
    print('Connected to server')
    sio.emit('message', 'Hello, server!')

def on_disconnect():
    print('Disconnected from server')

def on_message(data):
    print('Message from server:', data)

# Create a Socket.IO client instance
#sio = socketio.Client()
sio = socketio.Client(ssl_verify=False)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # this will silence the self signed cert warning
# Register event handlers
sio.on('connect', on_connect)
sio.on('disconnect', on_disconnect)
sio.on('message', on_message)

if __name__ == "__main__":
    sio.connect('https://pong:8888')
    sio.wait()
