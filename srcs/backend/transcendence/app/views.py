from django.shortcuts import render # redirect
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import logging
# from django.http import HttpResponse
# from django.core.exceptions import ValidationError
from .models import CustomUser
# from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate #, login, logout
from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm
from . import user

logger = logging.getLogger(__name__)

def register_user(request):
	if request.method == 'POST':
		logger.debug('In register user POST')
		response = user.registerPOST(request)
	elif request.method == 'GET':
		logger.debug('In register user GET')
		response = user.registerGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def login_user(request):
	logger.debug('In login_user()')
	if request.method == 'POST':
		response = user.loginPOST(request)
	elif request.method == 'GET':
		response = user.loginGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response


def logout_user(request):
	if request.method == 'POST':
		logger.debug('In logout user')
		response = user.logoutPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response


def get_current_username(request):
	logger.debug('In get_current_username()')
	if request.method == 'POST':
		username = user.get_current_usernamePOST(request)
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


def manage_account(request):
	logger.debug('In manage_account()')
	if request.method =='GET':
		response = user.manage_accountGET(request)
	elif request.method == 'POST':
		response = user.manage_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response

# only allow interaction if user has session
def delete_account(request):
	logger.debug('In delete_account()')
	if request.method == 'GET':
		response = user.delete_accountGET(request)
	elif request.method == 'POST':
		response = user.delete_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response
	
""" 
on account delete, how to handle other recodrs tied to that username? if the username isn't purged from all,
if another user uses it they will then be linked to the other records...
"""

def profile(request, username):
	self = False
	if request.user == username:
		self = True
	if request.method == "GET":
		friends = user.get_friends_dict(username)
		details = user.get_profile_details(username, self)
		context = {}
		context["friends"] = friends
		context["details"] = details
		context["email_form"] = UpdateEmailForm()
		context["password_form"] = UpdatePasswordForm()
		# need to add in the game stats and history here too
		if self:
			return render(request, 'user/profile_self.html', context)
		else:
			return render(request, 'user/profile_other.html', {})
	else:
		return JsonResponse({"message": "method not allowed, try GET"})

	