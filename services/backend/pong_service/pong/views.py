from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging

logger = logging.getLogger(__name__)

p1Score = 50  # Initial number
p2Score = 50

def add_cors_headers(response):
    response["Access-Control-Allow-Origin"] = "https://localhost"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
    response["Access-Control-Allow-Headers"] = "Content-Type"


@api_view(['GET']) 
def increase_number(request):
    global p1Score
    global p2Score

    # Increment the scores
    p1Score += 1
    p2Score += 1

    # Prepare the response
    response = {'successful increase'}                                                                
    return Response(response)

@api_view(['GET']) 
def decrease_number(request):
    global p1Score
    global p2Score
    p1Score -= 1
    p2Score -= 1
    response = {'successful decrease'}                                                                
    return Response(response)


@api_view(['GET']) 
def get_number(request):
    response = {'p1Score': p1Score, 'p2Score': p2Score}                                                                
    return Response(response)
