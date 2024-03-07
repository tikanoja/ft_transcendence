from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
# import json
from .models import CustomUser
from user.input_validation import validate_registration_input
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm


logger = logging.getLogger(__name__)

current_number = 42  # Initial number

# Added cors_middleware.py to do this automatically for all requests. Referencced in setting.py MIDDLEWARE
def add_cors_headers(response):
	response["Access-Control-Allow-Origin"] = "https://localhost"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
	response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-CSRFToken"
	response["Access-Control-Allow-Credentials"] = "true"

# @csrf_exempt
# def increase_number(request):
# 	logger.debug('In increase num')
# 	global current_number
# 	if request.method == 'POST':
# 		if (current_number < 100):
# 			current_number += 1
# 		response = JsonResponse({'result': 'success', 'number': current_number})
# 		return response
# 	else:
# 		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
# 		return response

# @csrf_exempt
# def decrease_number(request):
# 	logger.debug('In decrease num')
# 	global current_number
# 	if request.method == 'POST':
# 		if (current_number > 0):
# 			current_number -= 1
# 		response = JsonResponse({'result': 'success', 'number': current_number})
# 		return response
# 	else:
# 		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
# 		return response

# @csrf_exempt
# def get_number(request):
# 	logger.debug('In get num')
# 	global current_number
# 	response = JsonResponse({'result': 'success', 'number': current_number})
# 	return response

def	register(request):
	form = RegistrationForm()
	title = "Register as a new user"
	return render(request, 'registration_form', {"form": form, "title": title})


# @csrf_exempt
def register_user(request):
	if request.method == 'POST':
		logger.debug('In register user')
		# data = json.loads(request.body)
		data = request.POST
		logger.debug(data)
		# call for validation
		try:
			validate_registration_input(data)
		except ValueError as ve:
			logger.debug(f"Error in registration form: {ve}")
			form = RegistrationForm()
			title = "Register as a new user"
			# resend reg form with error msg included
			return render(request, 'registration', {"form": form, "title": title, "error_msg": ve})
		# pass validated user for database entry

		new_user = CustomUser(username=data["username"], firstname=data["firstname"], lastname=data["lastname"], email=data["email"], password=data["password"])
		logger.debug(new_user.username)
		logger.debug(new_user.firstname)
		logger.debug(new_user.lastname)
		logger.debug(new_user.email)
		logger.debug(new_user.password)
		
		new_user = get_user_model()
		if new_user.objects.filter(username=data['username']).exists():
			response = JsonResponse({'error': 'Username already exists.'}, status=400)
		else:
			new_user.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
			response = JsonResponse({'message': 'congrats you registered!'})	
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response

@csrf_exempt
def login_user(request):
	if request.method == 'POST':

		logger.debug('In login user')
		# data = json.loads(request.body)
		data = request.POST
		username = data['username']
		password = data['password']
		if request.user.is_authenticated:
			response = JsonResponse({'error': "already logged in!"})
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
	return response

@csrf_exempt
def logout_user(request):
	if request.method == 'POST':
		logger.debug('In logout user')
		if request.user.is_authenticated:
			logout(request)
			response = JsonResponse({'success': "Logged out!"})
		else:
			response = JsonResponse({'error': "User is not logged in."}, status=401)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response

@csrf_exempt
def get_current_username(request):
	logger.debug('In get_current_username()')
	origin = request.headers.get("Origin")
	logger.debug('The origin for the request was: ' + origin)
	if request.method == 'POST':
		if request.user.is_authenticated: #The responnse comes with the session ID var stored in the browser and django automatically figures out which user this ID belongs to
			username = request.user.username
		else:
			username = 'unknown user'
	else:
		username = 'only POST allowed'
	response = JsonResponse({'message': username})
	return response

# @csrf_exempt
# def login_user(request):
# 	if request.method == 'POST':
# 		logger.debug('In login user')
# 		data = json.loads(request.body)
# 		logger.debug(data)
# 		username = data['username']
# 		password = data['password']
# 		user = authenticate(request, username=username, password=password)
# 		if user is not None:
# 			login(request, user)
# 			# store users id in session
# 			request.session['user_id'] = user.id
# 			response = HttpResponse("oh my god it actually worked!!!")
# 		else:
# 			response = HttpResponse("bad credentials. register or try again")
# 	else:
# 		# render login form here !!! :)
# 		response = HttpResponse("this is a login form believe it or not")
# 	add_cors_headers(response) #dose this work with http res?
# 	return response
