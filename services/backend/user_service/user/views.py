from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm, DeleteAccountForm


logger = logging.getLogger(__name__)

current_number = 42  # Initial number

# Added cors_middleware.py to do this automatically for all requests. Referencced in setting.py MIDDLEWARE
def add_cors_headers(response):
	response["Access-Control-Allow-Origin"] = "https://localhost"
	response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
	response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-CSRFToken"
	response["Access-Control-Allow-Credentials"] = "true"


@csrf_exempt
def increase_number(request):
	logger.debug('In increase num')
	global current_number
	if request.method == 'POST':
		if (current_number < 100):
			current_number += 1
		response = JsonResponse({'result': 'success', 'number': current_number})
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		return response


@csrf_exempt
def decrease_number(request):
	logger.debug('In decrease num')
	global current_number
	if request.method == 'POST':
		if (current_number > 0):
			current_number -= 1
		response = JsonResponse({'result': 'success', 'number': current_number})
		return response
	else:
		response = JsonResponse({'result': 'error', 'message': 'Invalid request method'})
		return response


@csrf_exempt
def get_number(request):
	logger.debug('In get num')
	global current_number
	response = JsonResponse({'result': 'success', 'number': current_number})
	return response


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


def manage_account(request):
	if request.method =='GET':
		# send the interfacet hat will send POST reqs here
		pass
	elif request.method == 'POST':
		# edit the user entry in db based off of info sent.
		# only if authenticated.
		pass

def delete_account(request, username):
	if request.method == 'GET':
		return JsonResponse({'message': 'This will have the form to fill and send for account deletion'})
	elif request.method == 'POST':
		if request.user.is_authenticated:
			delete_form = DeleteAccountForm(request.POST)
			if not delete_form.is_valid():
				return render(request, 'delete_account.html', {"form": delete_form, "error": "Values given are not valid"})
			username = request.user
			password = delete_form.cleaned_data["password"]
			user = authenticate(request, username=username, password=password)
			if user is not None:
				# check if this should cascade delete the profile etc. remove from friend lists...
				CustomUser.objects.filter(username=username).delete()
				# delete account, return a success page with a 'link' to go to homepage
				return JsonResponse({'message': 'Your account has been deleted'})
			else:
				return JsonResponse({'message': 'Unable to delete account. Check which account you are logged in as'})
		else:
			return JsonResponse({'message': 'User needs to be logged into delete account'})
	
""" 
on account delete, how to handle other recodrs tied to that username? if the username isn't purged from all,
if another user uses it they will then be linked to the other records...
"""