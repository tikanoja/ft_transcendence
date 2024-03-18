from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm

logger = logging.getLogger(__name__)

def	registerPOST(request):
	title = "Register as a new user"
	sent_form = RegistrationForm(request.POST)
	try:
		if not sent_form.is_valid():
			raise ValidationError("Form filled incorrectly")
	except ValidationError as ve:
		logger.debug(f"Error in registration form: {ve}")
		return render(request, 'user/register.html', {"form": sent_form, "title": title, "error": ve})
	new_user = CustomUser(username=sent_form.cleaned_data["username"], first_name=sent_form.cleaned_data["first_name"], last_name=sent_form.cleaned_data["last_name"], email=sent_form.cleaned_data["email"], password=sent_form.cleaned_data["password"])
	new_user = get_user_model()
	new_user.objects.create_user(username=sent_form.cleaned_data['username'], email=sent_form.cleaned_data['email'], password=sent_form.cleaned_data['password'])
	response = JsonResponse({'message': 'congrats you registered!'})
	return response


def registerGET(request):
	title = "Register as a new user"
	form = RegistrationForm()
	return render(request, 'user/register.html', {"form": form, "title": title})


def register_user(request):
	if request.method == 'POST':
		logger.debug('In register user POST')
		response = registerPOST(request)
	elif request.method == 'GET':
		logger.debug('In register user GET')
		response = registerGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def loginPOST(request):
	title = "Sign in"
	sent_form = LoginForm(request.POST)
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
		# response = JsonResponse({'success': "you just logged in"})
		res = JsonResponse({'success': "you just logged in"}, status=301)
		res['Location'] = "/play"
		logger.debug("sending back a response w code %s", res.status_code)
		return res
		# could send a redirect to the home page or user profile
	else:
		logger.debug("user not authenticated")
		return render(request, 'user/login.html', {"form": sent_form, "title": title, "error": "user not found"})


def loginGET(request):
	logger.debug('In loginGET()')
	title = "Sign in"
	# send a redirect to logout pg?
	if request.user.is_authenticated:
		return render(request, "user/logout.html", {}) #redirect to show game view
		# return redirect("/user/logout")
	logger.debug('hello, will send login form!')
	form = LoginForm()
	logger.debug(form)
	return render(request, 'user/login.html', {"form": form, "title": title})


def login_user(request):
	logger.debug('In login_user()')
	if request.method == 'POST':
		response = loginPOST(request)
	elif request.method == 'GET':
		response = loginGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response


def	logoutPOST(request):
	if request.user.is_authenticated:
		logout(request)
		response = JsonResponse({'success': "Logged out!"})
	else:
		response = JsonResponse({'error': "User is not logged in."}, status=401)
	return response


def logout_user(request):
	if request.method == 'POST':
		logger.debug('In logout user')
		response = logoutPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response


def	get_current_usernamePOST(request):
	if request.user.is_authenticated:
			username = request.user.username
	else:
		username = 'unknown user'
	return username

def get_current_username(request):
	logger.debug('In get_current_username()')
	if request.method == 'POST':
		username = get_current_usernamePOST(request)
	else:
		username = 'only POST allowed'
	response = JsonResponse({'message': username})
	return response



def check_login(request):
	logger.debug('In check_login()')
	if request.user.is_authenticated:
		return JsonResponse({'status': 'authenticated'})
	else:
		return JsonResponse({'status': 'not authenticated'}, status=401)


def manage_accountPOST(request):
	if request.user.is_authenticated:
		pass
	# edit the user entry in db based off of info sent.
	# only if authenticated.
	else:
		return JsonResponse({'message': 'User needs to be logged into make changes to account'})
	
	
def manage_accountGET(request):
		# send the interfacet hat will send POST reqs here
	user = CustomUser.objects.filter(username=request.user)
	# username = 
	# 
	password_form = UpdatePasswordForm()
	email_form = UpdateEmailForm()
	return render(request, "user/manage_account.html", {}) #"username"=user.get_field('username')


def manage_account(request):
	logger.debug('In manage_account()')
	if request.method =='GET':
		response = manage_accountGET(request)
	elif request.method == 'POST':
		response = manage_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def delete_accountGET(request):
	return JsonResponse({'message': 'This will have the form to fill and send for account deletion'})


def delete_accountPOST(request):
	if request.user.is_authenticated:
		delete_form = DeleteAccountForm(request.POST)
		try:
			if not delete_form.is_valid():
				raise ValidationError("Values given are not valid") 
		except ValidationError as ve:
			return render(request, 'user/delete_account.html', {"form": delete_form, "error": ve})
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


def delete_account(request, username):
	logger.debug('In delete_account()')
	if request.method == 'GET':
		response = delete_accountGET(request)
	elif request.method == 'POST':
		response = delete_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response
	
""" 
on account delete, how to handle other recodrs tied to that username? if the username isn't purged from all,
if another user uses it they will then be linked to the other records...
"""