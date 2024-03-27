import requests
import time

def get_game_state():
    try:
        response = requests.get("http://127.0.0.1:5000/state_update")  # Replace with your server address
        if response.status_code == 200:
            game_state = response.json().get('STATE')
            return game_state
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        game_state = get_game_state()
        
        if game_state:
            # Process the game state as needed
            print("Received Game State:", game_state)
        
        time.sleep(1)  # Adjust the delay based on your requirements

if __name__ == "__main__":
    main()
