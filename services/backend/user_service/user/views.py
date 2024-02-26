from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)

current_number = 42  # Initial number

def add_cors_headers(response):
	response["Access-Control-Allow-Origin"] = "https://localhost"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
	response["Access-Control-Allow-Headers"] = "Content-Type"

@csrf_exempt
def increase_number(request):
	logger.debug('In increase num')
	global current_number
	if request.method == 'POST':
		if (current_number < 100):
			current_number += 1
		response = JsonResponse({'result': 'success', 'number': current_number})
		add_cors_headers(response)
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		add_cors_headers(response)
		return response

@csrf_exempt
def decrease_number(request):
	logger.debug('In decrease num')
	global current_number
	if request.method == 'POST':
		if (current_number > 0):
			current_number -= 1
		response = JsonResponse({'result': 'success', 'number': current_number})
		add_cors_headers(response)
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		add_cors_headers(response)
		return response

@csrf_exempt
def get_number(request):
	logger.debug('In get num')
	global current_number
	response = JsonResponse({'result': 'success', 'number': current_number})
	add_cors_headers(response)
	return response
