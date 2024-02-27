from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.http import HttpRequest
import json
from user.models import User

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

@csrf_exempt
def register_user(request):
	if request.method == 'POST':
		logger.debug('In register user')
		data = json.loads(request.body)
		logger.debug(data)
		new_user = User(username=data["username"], firstname=data["firstname"], lastname=data["lastname"], email=data["email"], password=data["password"])
		logger.debug(new_user.username)
		logger.debug(new_user.firstname)
		logger.debug(new_user.lastname)
		logger.debug(new_user.email)
		logger.debug(new_user.password)

	response = HttpResponse("Congrats you registered!")
	add_cors_headers(response) #dose this work with http res?
	return response
