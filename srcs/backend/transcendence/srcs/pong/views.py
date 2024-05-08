from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import requests
from django.shortcuts import render

logger = logging.getLogger(__name__)
from rest_framework.response import Response

@csrf_exempt
def get_game_state(request):
    try:
        if request.method == 'POST':
            p1_username = request.POST.get('p1_username')
            p2_username = request.POST.get('p2_username')
            logger.debug(f"data: {p1_username}, {p2_username}")
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
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

def get_canvas_colorwar(request):
	logger.debug('In get_canvas_color()')
	if request.method == 'GET':
		logger.debug('about to render!')
		return render(request, "pong/colorwar.html", {})
		

