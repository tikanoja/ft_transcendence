from django.http import JsonResponse
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import logging
# import json
# import requests
from django.shortcuts import render
from . import utils
from app.models import PongGameInstance

logger = logging.getLogger(__name__)


@csrf_exempt
def save_game_state(request):
    logger.debug('in save_game_state')
    try:

        logger.debug('checking all game instances for pong')
        all_games = PongGameInstance.objects.all()
        logger.debug(all_games)
        if request.method == 'POST':
            game_type = request.POST.get('game')
            if game_type == 'Pong':
                response = utils.save_pong_game_state(request)
            else:
                response = JsonResponse({'message': 'Invalid game type!'}, status=400)
        elif request.method == 'GET':
            response = JsonResponse({'message': 'Hi from Django GET!'}, status=200)
        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def validate_match(request):
    try:
        if request.method == 'POST':
            p1_username = request.POST.get('p1_username')
            p2_username = request.POST.get('p2_username')
            logger.debug(f"data from validate user: {p1_username}, {p2_username}")
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def get_canvas(request):
	logger.debug('In get_canvas()')
	if request.method == 'GET':
		logger.debug('about to render!')
		return render(request, "pong/pong.html", {})
		

