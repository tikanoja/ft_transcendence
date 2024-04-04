from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, AddFriendForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .models import CustomUser, Friendship
from django.core.exceptions import ValidationError
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import Q
import json

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
    res = JsonResponse({'success': "account created"}, status=301)
    next = request.GET.get('next', '/login')
    if next:
        res['Location'] = next
    return res


def registerGET(request):
    title = "Register as a new user"
    form = RegistrationForm()
    return render(request, 'user/register.html', {"form": form, "title": title})


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
        next = request.GET.get('next', '/play')
        if next:
            res['Location'] = next
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


def	logoutPOST(request):
    if request.user.is_authenticated:
        logout(request)
        next = request.GET.get('next', '/login')
        return HttpResponseRedirect(next)	
    else:
        response = JsonResponse({'error': "Already logged out."})
    return response

def	get_current_usernamePOST(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'unknown user'
    return username


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


def friendsContext(request, error, success):
    logger.debug('in friendsContext')
    form = AddFriendForm()
    title = "Manage friends"
    current_user = request.user

    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))

    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)

    if not error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships}
    elif error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'error': error}
    else:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'success': success}
    return context

def friendsGET(request):
    form = AddFriendForm()
    title = "Manage friends"
    current_user = request.user

    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))

    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)

    context = {
        'current_user': current_user,
        'form': form,
        'title': title,
        'in_invites': in_invites,
        'out_invites': out_invites,
        'friendships': friendships,
    }
    return render(request, 'user/friends.html', context)	


def friendResponse(request, data):
    from_username = data.get('from_user')
    from_user = CustomUser.objects.filter(username=from_username).first()
    if not from_user:
        return render(request, 'user/friends.html', friendsContext(request, "Could not find the friend candidate", None))    
    action = data.get('action')
    friendship = Friendship.objects.filter(Q(to_user=request.user, from_user=from_user) | Q(to_user=from_user, from_user=request.user)).first()
    if not friendship:
        return render(request, 'user/friends.html', friendsContext(request, "Could not find the friendship", None))    

    if action == 'accept':
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        return render(request, 'user/friends.html', friendsContext(request, None, "Congratulations, you made a new friend!"))
    elif action == 'reject':
        friendship.delete()
        return render(request, 'user/friends.html', friendsContext(request, None, "Friendship REJECTED!"))
    elif action == 'delete':
        friendship.delete()
        return render(request, 'user/friends.html', friendsContext(request, None, "Friendship DELETED!"))


def friendsPOST(request):
    logger.debug('in friendsPOST')
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('request_type') == 'friendResponse':
            return friendResponse(request, data)
        else:
            return render(request, 'user/friends.html', friendsContext(request, ve, "Unknown content type"))

    sent_form = AddFriendForm(request.POST)
    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/friends.html', friendsContext(request, ve, None))
    friend_username = sent_form.cleaned_data['username']

    # check if they are trying to add themselves
    if request.user.username == friend_username:
        return render(request, 'user/friends.html', friendsContext(request, "Please do not add yourself", None))

    current_user = request.user
    friend_user = CustomUser.objects.filter(username=friend_username).first()
    # all friendships where current_user is: no matter the status
    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))
    # all accepted friendships where current_user is
    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    # pending friend requests coming for current_user
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    # the request current_user has sent out to other users
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)

    # check if they are already friends
    if friendships.filter(Q(from_user=friend_user) | Q(to_user=friend_user)):
        return render(request, 'user/friends.html', friendsContext(request, "You are already friends", None))

    # check if friend_user matches an incoming invite, and if yes, update the status of that Friendship to ACCEPTED
    incoming_invite = in_invites.filter(from_user=friend_user)
    if incoming_invite.exists():
        incoming_invite.update(status=Friendship.ACCEPTED)
        return render(request, 'user/friends.html', friendsContext(request, None, "Congratulations, you made a new friend!"))

    # check if they have already sent a request to the user in question
    if out_invites.filter(to_user=friend_user):
        return render(request, 'user/friends.html', friendsContext(request, "You have already sent a request to this user", None))

    # add to friends
    new_friendship = Friendship(from_user=current_user, to_user=friend_user, status=Friendship.PENDING)
    new_friendship.save()

    return render(request, 'user/friends.html', friendsContext(request, None, "Friend request sent"))