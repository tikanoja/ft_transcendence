from django.shortcuts import render # redirect
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import logging
# from django.http import HttpResponse
# from django.core.exceptions import ValidationError
from .models import CustomUser
# from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate #, login, logout
from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, UploadImageForm
from . import user
from django.contrib.auth.decorators import login_required
from django.db.models import Q


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
	if request.method == 'GET':
		username = user.get_current_usernameGET(request)
	else:
		username = 'only GET allowed'
	response = JsonResponse({'message': username})
	return response


def check_login(request):
	logger.debug('In check_login()')
	if request.user.is_authenticated:
		return JsonResponse({'status': 'authenticated'})
	else:
		return JsonResponse({'status': 'not authenticated'})

# POST only
# returns JSON resonse with result of form handling success or error
def manage_account(request):
	logger.debug('In manage_account()')
	if request.method =='POST':
		response = user.manage_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response

# only allow interaction if user has session
# def delete_account(request):
# 	logger.debug('In delete_account()')
# 	if request.method == 'GET':
# 		response = user.delete_accountGET(request)
# 	elif request.method == 'POST':
# 		response = user.delete_accountPOST(request)
# 	else:
# 		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
# 	return response


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


@login_required
def play(request):
	logger.debug('In play()')
	if request.method == 'GET':
		response = user.playGET(request)
	elif request.method == 'POST':
		response = user.playPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


@login_required
def friends(request):
	logger.debug('In friends()')
	if request.method == 'GET':
		response = user.friendsGET(request)
	elif request.method == 'POST':
		response = user.friendsPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


@login_required
def home(request):
	logger.debug('In home()')
	if request.method == 'GET':
		return render(request, 'user/home.html', {})
	elif request.method == 'POST':
		response = user.playPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def notfound(request):
	logger.debug('in notfound()')
	if request.method == 'GET':
		return render(request, 'user/404.html', {})
	else:
		return JsonResponse({'error': "method not allowed. please use GET"})


def profile(request, username):
	logger.debug('getting profile')
	self = False
	if request.user.username == username:
		self = True
	if request.method == "GET":
		friends = user.friendsContext(username, None, None)
		logger.debug(friends)
		details = user.get_profile_details(username, self)
		context = {}
		context["friends"] = friends #TODO get the friends context from Tuukka's friend stuff
		context["details"] = details
		context["name_form"] = UpdateNameForm()
		context["email_form"] = UpdateEmailForm()
		context["password_form"] = UpdatePasswordForm()
		context["delete_account_form"] = DeleteAccountForm()
		context["upload_image_form"] = UploadImageForm()
		context["self_profile"] = self
		try:
			profile_user = CustomUser.objects.filter(username=username).first()
			if profile_user:
				context["profile_picture"] = profile_user.profile_picture
		except Exception as e:
			logger.debug('error: ', e)
			logger.debug('unable to search image')
		# need to add in the game stats and history here too
		return render(request, 'user/profile.html', context)
	else:
		return JsonResponse({"message": "method not allowed, try GET"})

