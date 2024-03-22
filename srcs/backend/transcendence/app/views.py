from django.shortcuts import render # redirect
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import logging
# from django.http import HttpResponse
# from django.core.exceptions import ValidationError
from .models import CustomUser
# from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate #, login, logout
# from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm
from . import user
from django.contrib.auth.decorators import login_required

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
		return JsonResponse({'status': 'not authenticated'})


def manage_account(request):
	logger.debug('In manage_account()')
	if request.method =='GET':
		response = user.manage_accountGET(request)
	elif request.method == 'POST':
		response = user.manage_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def delete_account(request, username):
	logger.debug('In delete_account()')
	if request.method == 'GET':
		response = user.delete_accountGET(request)
	elif request.method == 'POST':
		response = user.delete_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response

@login_required
def settings(request):
	logger.debug('In settings()')
	if request.method == 'GET':
		return render(request, 'user/settings.html', {})
	elif request.method == 'POST':
		response = user.settingsPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response

def notfound(request):
	logger.debug('in notfound()')
	if request.method == 'GET':
		return render(request, 'user/404.html', {})
	else:
		return JsonResponse({'error': "method not allowed. please use GET"})

""" 
on account delete, how to handle other recodrs tied to that username? if the username isn't purged from all,
if another user uses it they will then be linked to the other records...
"""