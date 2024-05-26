from django.contrib.auth import authenticate, login, logout
from app.forms import LoginForm
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
import logging
from app.models import CustomUser


logger = logging.getLogger(__name__)


def loginPOST(request):
    title = "Sign in"
    sent_form = LoginForm(request.POST)
    sent_form.is_valid()
    username = sent_form.cleaned_data['username']
    password = sent_form.cleaned_data['password']
    if request.user.is_authenticated:
        response = JsonResponse({'error': "already logged in!"}, status=200)
        return response
    user_check = CustomUser.objects.filter(username=username).first()
    if user_check is None:
        return render(request, 'user/login.html', {"form": sent_form, "title": title, "error": "user not found!"})
    user = authenticate(request, username=username, password=password) #verifiy credentials, if match with db, returns user object
    if user is not None:
        login(request, user) #log user in, create new session, add sessionID cookie for the response
        request.session['user_id'] = user.id #store user ID explicity to the request.session dictionary
        user.is_online = True
        user.save()
        res = JsonResponse({'success': "you just logged in"}, status=301)
        next = request.GET.get('next', '/play')
        if next:
            res['Location'] = next
        return res
        # could send a redirect to the home page or user profile
    else:
        return render(request, 'user/login.html', {"form": sent_form, "title": title, "error": "wrong password!"})


def loginGET(request):
    title = "Sign in to play!"
    # send a redirect to logout pg?
    if request.user.is_authenticated:
        return render(request, 'user/logged_in.html', {"current_user": request.user})
    form = LoginForm()
    next = request.GET.get('next', '/play')
    res = render(request, 'user/login.html', {"form": form, "title": title})
    if next:
        res['Location'] = next
    return res


def	logoutPOST(request):
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.save()
        logout(request)
        next = request.GET.get('next', '/login')
        return HttpResponseRedirect(next)	
    else:
        response = JsonResponse({'error': "Already logged out."}, status=200)
    return response


def	get_current_usernameGET(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'unknown user'
    return username
