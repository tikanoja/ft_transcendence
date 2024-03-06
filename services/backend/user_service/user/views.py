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
		new_user = get_user_model()
		if new_user.objects.filter(username=data['username']).exists():
			response = JsonResponse({'error': 'Username already exists.'}, status=400)
		else:
			new_user.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
			response = JsonResponse({'message': 'congrats you registered!'})	
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	add_cors_headers(response) #dose this work with http res?
	return response

@csrf_exempt
def login_user(request):
	if request.method == 'POST':
		logger.debug('In login user')
		data = json.loads(request.body)
		username = data['username']
		password = data['password']
		if request.user.is_authenticated:
			response = JsonResponse({'error': "already logged in!"})
			add_cors_headers(response)
			return response
		user = authenticate(request, username=username, password=password) #verifiy credentials, if match with db, returns user object
		if user is not None:
			login(request, user) #log user in, create new session, add sessionID cookie for the response
			request.session['user_id'] = user.id #store user ID explicity to the request.session dictionary
			response = JsonResponse({'success': "you just logged in"})
		else:
			response = JsonResponse({'error': "user not found"}, status=401)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	add_cors_headers(response)
	return response

@csrf_exempt
def logout_user(request):
	logger.debug('HERE!!!!!')
	if request.method == 'POST':
		logger.debug('In logout user')
		if request.user.is_authenticated:
			logout(request)
			response = JsonResponse({'success': "Logged out!"})
		else:
			response = JsonResponse({'error': "User is not logged in."}, status=401)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	add_cors_headers(response) #dose this work with http res?
	return response

@csrf_exempt
def get_current_username(request):
	logger.debug('In get_current_username()')
	if request.method == 'POST':
		if request.user.is_authenticated: #The responnse comes with the session ID var stored in the browser and django automatically figures out which user this ID belongs to
			username = request.user.username
		else:
			username = 'unknown user'
	else:
		username = 'only POST allowed'
	response = JsonResponse({'message': username})
	add_cors_headers(response)
	return response
