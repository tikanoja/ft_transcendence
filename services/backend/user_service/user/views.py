from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.http import HttpRequest
import json
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout

logger = logging.getLogger(__name__)

current_number = 42  # Initial number

def add_cors_headers(response):
	response["Access-Control-Allow-Origin"] = "https://localhost"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
	response["Access-Control-Allow-Headers"] = "Content-Type"
	response["Access-Control-Allow-Credentials"] = "true"

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
		new_user = get_user_model()
		new_user.objects.create_user(username=data['username'], email=data['email'], password=data['password'])

	response = JsonResponse({'message': 'congrats you registered!'})	
	add_cors_headers(response) #dose this work with http res?
	return response

@csrf_exempt
def login_user(request):
	if request.method == 'POST':
		logger.debug('In login user')
		data = json.loads(request.body)
		logger.debug(data)
		username = data['username']
		password = data['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			# store users id in session
			request.session['user_id'] = user.id
			response = JsonResponse({'message': "oh my god it actually worked!!!"})
		else:
			response = JsonResponse({'error': "bad credentials. register or try again"}, status=401)
	else:
		# render login form here !!! :)
		response = JsonResponse({'message': "this is a login form believe it or not"})
	add_cors_headers(response) #dose this work with http res?
	return response

@csrf_exempt
def logout_user(request):
	if request.method == 'POST':
		logger.debug('In logout_user()')
		logout(request, user)
	response = JsonResponse({'message': "logged out!"})
	add_cors_headers(response) #dose this work with http res?
	return response

@csrf_exempt
def get_current_username(request):
	logger.debug('In get_current_username()')
	if request.method == 'POST':
		if request.user.is_authenticated: #The responnse comes with the session ID var stored in the browser and django automatically figures out which user this ID belongs to
			username = request.user.username
		else:
			username = 'you are not logged in'
	else:
		username = 'only POST allowed'
	response = JsonResponse({'hello': username})
	add_cors_headers(response)
	return response
