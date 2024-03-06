from django.shortcuts import render
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

@csrf_exempt
def increase_number(request):
	logger.debug('In increase num')
	global p1Score
	if request.method == 'POST':
		if (p1Score < 100):
			p1Score += 1
		response = JsonResponse({'result': 'success', 'number': p1Score})
		add_cors_headers(response)
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		add_cors_headers(response)
		return response

@csrf_exempt
def decrease_number(request):
	logger.debug('In decrease num')
	global p1Score
	if request.method == 'POST':
		if (p1Score > 0):
			p1Score -= 1
		response = JsonResponse({'result': 'success', 'number': p1Score})
		add_cors_headers(response)
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		add_cors_headers(response)
		return response



@api_view(['GET'])  # Decorator to specify HTTP methods allowed
def get_number(request):
	logger.debug('In get num')
	score = {'p1Score': p1Score, 'p2Score': p2Score}
	add_cors_headers(score)
	return Response(score)


# # this is the placeholder now for scores
# @csrf_exempt 
# def get_number(request):
# 	logger.debug('In get num')
# 	global p1Score
# 	global p2Score
# 	response = JsonResponse({'result': 'success', 'p1Score': p1Score, 'p2Score': p2Score})
# 	return response
