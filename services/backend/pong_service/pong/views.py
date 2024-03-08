from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging

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

@api_view(['GET']) 
def decrease_number(request):
    global p1_score
    global p2_score
    p1_score -= 1
    p2_score -= 1
    response = {'successful decrease'}                                                                
    return Response(response)


@api_view(['GET'])
def get_game_state(request):
    global p1_x_pos
    global p2_x_pos
    global p1_score
    global p2_score
    global p1_y_pos
    global p2_y_pos
    global game_progress
    response = {'game_progress': game_progress , 'p1_pos_y': p1_y_pos, 'p2_pos_y': p2_y_pos, 'p1_pos': p1_x_pos, 'p2_pos': p2_x_pos, 'p1_score': p1_score, 'p2_score': p2_score}
    return Response(response)


@api_view(['GET']) 
def decrease_number(request):
    global p1_score
    global p2_score
    p1_score -= 1
    p2_score -= 1
    response = {'successful decrease'}                                                                
    return Response(response)


@api_view(['GET']) 
def get_number(request):
    response = {'p1_score': p1_score, 'p2_score': p2_score}                                                                
    return Response(response)
