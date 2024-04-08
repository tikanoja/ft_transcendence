from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, AddFriendForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .models import CustomUser, CustomUserManager, GameInstance, Friendship
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
    new_user = get_user_model()
    new_user.objects.create_user(username=sent_form.cleaned_data['username'], email=sent_form.cleaned_data['email'], password=sent_form.cleaned_data['password'], first_name=sent_form.cleaned_data['first_name'], last_name=sent_form.cleaned_data['last_name'])
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


def delete_accountGET(request):
    return JsonResponse({'message': 'This will have the form to fill and send for account deletion'})


def delete_accountPOST(request):
    if request.user.is_authenticated:
        delete_form = DeleteAccountForm(request.POST)
        try:
            if not delete_form.is_valid():
                raise ValidationError("Values given are not valid") 
        except ValidationError as ve:
            return render(request, 'user/profile_partials/delete_account.html', {"form": delete_form, "error": ve})
        username = request.user
        password = delete_form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # check if this should cascade delete the profile etc. remove from friend lists...
            Friendship.objects.filter(from_user=username).delete()
            Friendship.objects.filter(to_user=username).delete()
            CustomUser.objects.filter(username=username).delete()
            # delete account, return a success page with a 'link' to go to homepage
            return JsonResponse({'message': 'Your account has been deleted'})
        else:
            return JsonResponse({'message': 'Unable to delete account. Check which account you are logged in as'})
    else:
        return JsonResponse({'message': 'User needs to be logged into delete account'})


def manage_accountPOST(request):
    user_manager = CustomUserManager()
    logger.debug(request.POST)
    if "name-change-form" == request.POST['form_id']:
        logger.debug("name change form found")
        form = UpdateNameForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
        except ValidationError as ve:
            return JsonResponse({'message': ve})
        user_manager.update_user(request.user.username, first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"])
        return JsonResponse({'message': f'Name updated successfully'})
    elif "email-change-form" == request.POST['form_id']:
        logger.debug("email change form found")
        form = UpdateEmailForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
        except ValidationError as ve:
            return JsonResponse({'message': ve})
        user_manager.update_user(request.user.username, email=form.cleaned_data["email"])
        return JsonResponse({'message': f'Email updated successfully'})
    elif "password-change-form" == request.POST['form_id']:
        logger.debug("password change form found")
        form = UpdatePasswordForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
        except ValidationError as ve:
            return JsonResponse({'message': ve})
        user_manager.update_user(request.user.username, password=form.cleaned_data["password"])
        return JsonResponse({'message': f'Password updated successfully'})
    elif "delete-account-form" == request.POST['form_id']:
        return delete_accountPOST(request)
    else:
        return JsonResponse({'message': 'Invalid form submitted'})
    

# basic details username, name, image link, other public viewable stuff
# email, other spcific things? for self view
def get_profile_details(username:str, self:bool) -> dict:
    details = {}
    user = CustomUser.objects.filter(username=username)
    if not user:
        details["error"] = "No users in system match the requested user"
    else:
        details["username"] = username
        details["first_name"] = user[0].first_name
        details["last_name"] = user[0].last_name
        if self:
            details["email"] = user[0].email
    # details["img"] = user.img #how to get link for profile image?
    print(details)
    return details


# hadcode a dict of friends for now
# does self matter for this one?
def get_friends_dict(username:str) -> dict:
    user = CustomUser.objects.filter(username=username)
    # will get friends list from the user
    friends = [
        {
            "username": "username1",
            "picture_link": "picture_link"
        },
        {
            "username": "username2",
            "picture_link": "picture_link"
        }
    ]
    return friends


def get_game_result(self_score: int, opponent_score: int) -> str:
    if self_score < opponent_score:
        return "Won"
    elif self_score == opponent_score:
        return "Tie"
    else:
        return "Lost"


def get_game_history(username:str) -> dict:
    user = CustomUser.objects.get(username=username)
    u1_games = GameInstance.objects.filter(p1_user=user)
    u2_games = GameInstance.objects.filter(p2_user=user)
    all_games = u1_games.union(u2_games)
    history = {}
    for iter, game in enumerate(all_games):
        entry = {}
        entry["game"] = game.game
        entry["date"] = game.date
        if game.p1_user == user:
            entry["opponent"] = game.p2_user
            entry["result"] = get_game_result(game.p1_score, game.p2_score)
        else:
            entry["opponent"] = game.p1_user
            entry["result"] = get_game_result(game.p2_score, game.p1_score)
        history[iter] = entry
    return history


def get_dashboard_stats(username:str) -> dict:
    user = CustomUser.objects.get(username=username)
    u1_games = GameInstance.objects.filter(p1_user=user)
    u2_games = GameInstance.objects.filter(p2_user=user)
    all_games = u1_games.union(u2_games)
    pass

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
