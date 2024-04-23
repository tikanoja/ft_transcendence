from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
import json
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)


@csrf_exempt
def get_game_state(request):
    logger.debug("in get_game_state")
    try:
        if request.method == 'POST':
            logger.debug(request.POST)
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "An error occurred"}, status=500)

def get_canvas(request):
    logger.debug('In get_canvas()')
    if request.method == 'GET':
        logger.debug('about to render!')
        return render(request, "pong/3dgen.html", {})
        

