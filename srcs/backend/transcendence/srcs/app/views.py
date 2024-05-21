from django.shortcuts import render
from django.http import JsonResponse
import logging
# from django.contrib.auth import authenticate
from app.user import session, account, relations
from app.user import profile as user_profile
from django.contrib.auth.decorators import login_required

from .play import playGET, playPOST

logger = logging.getLogger(__name__)


def register_user(request):
	if request.method == 'POST':
		logger.debug('In register user POST')
		response = account.registerPOST(request)
	elif request.method == 'GET':
		logger.debug('In register user GET')
		response = account.registerGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def login_user(request):
	logger.debug('In login_user()')
	if request.method == 'POST':
		response = session.loginPOST(request)
	elif request.method == 'GET':
		response = session.loginGET(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response


def logout_user(request):
	if request.method == 'POST':
		logger.debug('In logout user')
		response = session.logoutPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST"})
	return response

# TODO: this needs to return the correct status code based on the situation
def get_current_username(request):
	logger.debug('In get_current_username()')
	if request.method == 'GET':
		username = session.get_current_usernameGET(request)
	else:
		username = 'only GET allowed'
	response = JsonResponse({'message': username})
	return response


def check_login(request):
	logger.debug('In check_login()')
	if request.is_authenticated:
		return JsonResponse({'status': 'authenticated'})
	else:
		return JsonResponse({'status': 'not authenticated'})

# POST only
# returns JSON resonse with result of form handling success or error
@login_required
def manage_account(request):
	logger.debug('In manage_account()')
	if request.method =='POST':
		response = account.manage_accountPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. Please use POST"}, status=405)
	return response

# only allow interaction if user has session
# def delete_account(request):
# 	logger.debug('In delete_account()')
# 	if request.method == 'GET':
# 		response = delete_accountGET(request)
# 	elif request.method == 'POST':
# 		response = delete_accountPOST(request)
# 	else:
# 		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
# 	return response


@login_required
def play(request):
	logger.debug('In play()')
	if request.method == 'GET':
		response = playGET(request)
	elif request.method == 'POST':
		response = playPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"}, status=405)
	return response


@login_required
def friends(request):
	logger.debug('In friends()')
	if request.method == 'GET':
		response = relations.friendsGET(request)
	elif request.method == 'POST':
		response = relations.friendsPOST(request)
	else:
		response = JsonResponse({'error': "method not allowed. please use POST or GET"})
	return response


def notfound(request):
	logger.debug('in notfound()')
	if request.method == 'GET':
		# check for current_user
		context = {}
		context["current_user"] = request.user.username
		return render(request, '404.html', context)
	else:
		return JsonResponse({'error': "method not allowed. please use GET"})

@login_required
def profile(request, username):
	logger.debug('getting profile')
	if request.method == "GET":
		if not user_profile.user_exists(username):
			return render(request, '404.html', {"current_user": request.user.username})
		self = False
		if request.user.username == username:
			self = True
		context = user_profile.profileContext(username, self)
		context["current_user"] = request.user.username
		return render(request, 'user/profile.html', context)
	else:
		return JsonResponse({"message": "method not allowed, try GET"})

@login_required
def profile_picture(request):
	if request.method == "GET":
		context = user_profile.get_profile_picture_context(request.user.username)
		response = render(request, "user/profile_partials/profile_picture.html", context)
	else:
		response = JsonResponse({'error': "method not allowed. Please use GET"}, status=405)
	return response