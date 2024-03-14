from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm


logger = logging.getLogger(__name__)

def register_user(request):
	title = "Register as a new user"
	if request.method == 'POST':
		logger.debug('In register user')#
		sent_form = RegistrationForm(request.POST)
		logger.debug(sent_form)#

		try:
			if not sent_form.is_valid():
				raise ValidationError("Form filled incorrectly")
		except ValidationError as ve:
			logger.debug(f"Error in registration form: {ve}")#
			return render(request, 'register.html', {"form": sent_form, "title": title, "error_msg": ve})
		# pass validated user for database entry
		new_user = CustomUser(username=sent_form.cleaned_data["username"], first_name=sent_form.cleaned_data["first_name"], last_name=sent_form.cleaned_data["last_name"], email=sent_form.cleaned_data["email"], password=sent_form.cleaned_data["password"])
		new_user = get_user_model()
		new_user.objects.create_user(username=sent_form.cleaned_data['username'], email=sent_form.cleaned_data['email'], password=sent_form.cleaned_data['password'])
		response = JsonResponse({'message': 'congrats you registered!'})
	elif request.method == 'GET':
			logger.debug('hello getting reg form!')#
			form = RegistrationForm()
			return render(request, 'register.html', {"form": form, "title": title})
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


# @csrf_exempt
def login_user(request):
	title = "Sign in"
	if request.method == 'POST':#
		logger.debug('In login user')
		sent_form = LoginForm(request.POST)
		logger.debug(sent_form)#
		sent_form.is_valid()
		username = sent_form.cleaned_data['username']
		password = sent_form.cleaned_data['password']
		if request.user.is_authenticated:
			response = JsonResponse({'error': "already logged in!"})
			return response
		user = authenticate(request, username=username, password=password) #verifiy credentials, if match with db, returns user object
		if user is not None:
			login(request, user) #log user in, create new session, add sessionID cookie for the response
			request.session['user_id'] = user.id #store user ID explicity to the request.session dictionary
			response = JsonResponse({'success': "you just logged in"})
			# could send a redirect to the home page or user profile
		else:
			return render(request, 'login.html', {"form": sent_form, "title": title, "error": "user not found"})
	elif request.method == 'GET':
		# send a redirect to logout pg?
		if request.user.is_authenticated:
			return render(request, "logout.html", {})
			# return redirect("/user/logout")
		logger.debug('hello, will send login form!')
		form = LoginForm()
		logger.debug(form)
		return render(request, 'login.html', {"form": form, "title": title})
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

def check_login(request):
	if request.user.is_authenticated:
		return JsonResponse({'status': 'authenticated'})
	else:
		return JsonResponse({'status': 'not authenticated'}, status=401)

