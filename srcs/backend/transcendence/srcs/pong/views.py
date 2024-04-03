from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
import json
import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)

p1_score = 50
p2_score = 50
p1_x_pos = 70
p2_x_pos = -100
p1_y_pos = 0
p2_y_pos = 0
game_progress = "In Progress"

@api_view(['GET']) 
def increase_number(request):
    global p1_score
    global p2_score
    global p1_y_pos
    global p2_y_pos

    p1_y_pos += 0.2
    p2_y_pos += 0.2
    p1_score += 1
    p2_score += 1

    response = {'successful increase'}                                                                
    return Response(response)

# @api_view(['GET'])
# def get_game_state(request):
#     global p1_x_pos
#     global p2_x_pos
#     global p1_score
#     global p2_score
#     global p1_y_pos
#     global p2_y_pos
#     global game_progress
#     response = {'game_progress': game_progress , 'p1_pos_y': p1_y_pos, 'p2_pos_y': p2_y_pos, 'p1_pos': p1_x_pos, 'p2_pos': p2_x_pos, 'p1_score': p1_score, 'p2_score': p2_score}
#     return Response(response)


@api_view(['GET']) 
def decrease_number(request):
    global p1_score
    global p2_score
    global p1_y_pos
    global p2_y_pos

    p1_y_pos -= 0.2
    p2_y_pos -= 0.2
    p1_score -= 1
    p2_score -= 1

    response = {'successful increase'}                                                                
    return Response(response)

# api.add_resource(StartGame, '/game_start/<int:number>')
@api_view(['GET']) #I need a way to have this working on multiple games
def game_start(request): 
    try:
        response = requests.get('http://pong_c:8080/game_start/0')
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)
    
@api_view(['GET']) #I need a way to have this working on multiple games
def game_stop(request): 
    try:
        response = requests.get('http://pong_c:8080/game_stop/0')
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)

# api.add_resource(LeftPaddleUp, '/left_paddle_up/<int:number>')
@api_view(['GET']) 
def left_paddle_up(request): 
    try:
        response = requests.get('http://pong_c:8080/left_paddle_up/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(LeftPaddleUpRelease, '/left_paddle_up_release/<int:number>')
@api_view(['GET']) 
def left_paddle_up_release(request): 
    try:
        response = requests.get('http://pong_c:8080/left_paddle_up_release/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(LeftPaddleDown, '/left_paddle_down/<int:number>')
@api_view(['GET']) 
def left_paddle_down(request): 
    try:
        response = requests.get('http://pong_c:8080/left_paddle_down/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(LeftPaddleDownRelease, '/left_paddle_down_release/<int:number>')
@api_view(['GET']) 
def left_paddle_down_release(request): 
    try:
        response = requests.get('http://pong_c:8080/left_paddle_down_release/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(RightPaddleUp, '/right_paddle_up/<int:number>')

@api_view(['GET']) 
def right_paddle_up(request): 
    try:
        response = requests.get('http://pong_c:8080/right_paddle_up/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(RightPaddleUpRelease, '/right_paddle_up_release/<int:number>')
@api_view(['GET']) 
def right_paddle_up_release(request): 
    try:
        response = requests.get('http://pong_c:8080/right_paddle_up_release/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(RightPaddleDown, '/right_paddle_down/<int:number>')
@api_view(['GET']) 
def right_paddle_down(request): 
    try:
        response = requests.get('http://pong_c:8080/right_paddle_down/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(RightPaddleDownRelease, '/right_paddle_down_release/<int:number>')
@api_view(['GET']) 
def right_paddle_down_release(request): 
    try:
        response = requests.get('http://pong_c:8080/right_paddle_down_release/0') #TODO: needs to handle which game thread
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(StartBackgroundLoop, '/start_background_loop')
@api_view(['GET']) 
def start_background_loop(request): 
    logger.debug('in start_backgroud_loop')
    print('in start back loop')
    try:
        response = requests.get('http://pong_c:8080/start_background_loop')
        logger.debug(response.text)
        return Response(response)
    except Exception as e:
        logger.debug(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)

# api.add_resource(StopBackgroundLoop, '/stop_background_loop')
@api_view(['GET']) 
def stop_background_loop(request): 
    try:
        response = requests.get('http://pong_c:8080/stop_background_loop')
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)

# api.add_resource(GamesRunning, '/games_running')
@api_view(['GET']) 
def get_games_running(request): 
    try:
        response = requests.get('http://pong_c:8080/games_running')
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


# api.add_resource(GetState, '/game_state/<int:number>')
@api_view(['GET']) 
def get_game_state(request):
    try:
        response = requests.get('http://pong_c:8080/game_state/0')
        print(response.text)
        return Response(response.json())
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)


@api_view(['GET']) 
def get_number(request):
    response = {'p1_score': p1_score, 'p2_score': p2_score}                                                                
    return Response(response)


def get_canvas(request):
	logger.debug('In get_canvas()')
	if request.method == 'GET':
		logger.debug('about to render!')
		return render(request, "pong/3dgen.html", {})
		

