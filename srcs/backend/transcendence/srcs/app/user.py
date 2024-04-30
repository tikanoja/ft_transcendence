from .forms import RegistrationForm, LoginForm, DeleteAccountForm, UpdatePasswordForm, UpdateEmailForm, UpdateNameForm, AddFriendForm, GameRequestForm, UploadImageForm
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
from django.utils import timezone
import os
from transcendence import settings

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
        user.is_online = True
        user.save()
        res = JsonResponse({'success': "you just logged in"}, status=301)
        next = request.GET.get('next', '/play')
        if next:
            res['Location'] = next
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
    form = LoginForm()
    logger.debug(form)
    return render(request, 'user/login.html', {"form": form, "title": title})


def	logoutPOST(request):
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.save()
        logout(request)
        next = request.GET.get('next', '/login')
        return HttpResponseRedirect(next)	
    else:
        response = JsonResponse({'error': "Already logged out."})
    return response

def	get_current_usernameGET(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'unknown user'
    return username


def delete_accountPOST(request, context):
    if request.user.is_authenticated:
        context["details"] = get_profile_details(request.user.username, True)
        delete_form = DeleteAccountForm(request.POST)
        try:
            if not delete_form.is_valid():
                raise ValidationError("Values given are not valid") 
        except ValidationError as ve:
            context["form"] = delete_form
            context["error"] = ve
            return render(request, "user/profile_partials/manage_account.html", context)
        username = request.user
        password = delete_form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # check if this should cascade delete the profile etc. remove from friend lists...
            Friendship.objects.filter(from_user=username).delete()
            Friendship.objects.filter(to_user=username).delete()
            GameInstance.objects.filter(p1=username, status='Pending').delete()
            GameInstance.objects.filter(p2=username, status='Pending').delete()
            CustomUser.objects.filter(username=username).delete()
            # delete account, return a success page with a 'link' to go to homepage
            return JsonResponse({'message': 'Your account has been deleted'})
        else:
            context["error"] = 'Unable to delete account. Check which account you are logged in as'
            return render(request, "user/profile_partials/manage_account.html", context)
    else:
        context["error"] = 'User needs to be logged into delete account'
        return render(request, "user/profile_partials/manage_account.html", context)

# basic details username, name, image link, other public viewable stuff
# email, other spcific things? for self view
def get_profile_details(username:str, self:bool) -> dict:
    details = {}
    user = CustomUser.objects.filter(username=username)
    logger.debug(user[0])
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

def create_manage_account_context(username: str) -> dict:
    context = {}
    # context["details"] = get_profile_details(username, self) want to add after any updates
    context["name_form"] = UpdateNameForm()
    context["email_form"] = UpdateEmailForm()
    context["password_form"] = UpdatePasswordForm()
    context["delete_account_form"] = DeleteAccountForm()
    context["upload_image_form"] = UploadImageForm()
    return context

# return dictionary for context with the resulting vars that can be rendered into the profile
def manage_accountPOST(request):
    user_manager = CustomUserManager()
    logger.debug(request.POST)
    context = create_manage_account_context(request.user.username)
    if "name-change-form" == request.POST['form_id']:
        logger.debug("name change form found")
        form = UpdateNameForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"])
            context["name_form_result"] = 'Name updated successfully'
        except ValidationError as ve:
            context["error"] = ve
            context["name_form"] = form
    elif "email-change-form" == request.POST['form_id']:
        logger.debug("email change form found")
        form = UpdateEmailForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, email=form.cleaned_data["email"])
            context['email_form_result'] = 'Email updated successfully'
        except ValidationError as ve:
            context["error"] = ve
            context["email_form"] = form 
    elif "password-change-form" == request.POST['form_id']:
        logger.debug("password change form found")
        form = UpdatePasswordForm(request.POST)
        try:
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly")
            user_manager.update_user(request.user.username, password=form.cleaned_data["password"])
            context['pasword_form_result'] = 'Password updated successfully. Please log back in with your new password'
        except ValidationError as ve:
            context["error"] = ve
            context["email_form"] = form 
    elif "delete-account-form" == request.POST['form_id']:
        return delete_accountPOST(request, context)
    elif "profile_picture_upload" == request.POST['form_id']:
        form = UploadImageForm(request.POST, request.FILES)
        try:
            current_user = CustomUser.objects.get(username=request.user.username)
            new_image = request.FILES['profile_picture']
            old_image = current_user.profile_picture
            if not form.is_valid():
                raise ValidationError("Form filled incorrectly for profile picture")
            if old_image.url != '/media/default.png':
                os.remove(os.path.join(settings.MEDIA_ROOT, old_image.path))
            current_user.profile_picture = new_image
            current_user.save()
            context['profile_picture_upload_message'] = 'new image uploaded!'
        except Exception as e:
            context["error"] = e
            context["profile_picture_upload"] = form 
    else:
        context["error"] = 'Invalid form submitted'
    context["details"] = get_profile_details(request.user.username, True)
    return render(request, "user/profile_partials/manage_account.html", context)
    

# hardcode a dict of friends for now
# does self matter for this one?


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


def friendsContext(username, error, success):
    logger.debug('in friendsContext')
    form = AddFriendForm()
    title = "Manage friends"
    # current_user = request.user
    current_user = CustomUser.objects.filter(username=username).first()

    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))

    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)
    blocked_users = current_user.blocked_users.all()
    logger.debug(blocked_users) #

    for friendship in friendships:
        other_user = friendship.from_user if friendship.from_user != current_user else friendship.to_user
        logger.debug('username: ' + other_user.username + ', last seen at: ' + other_user.last_seen.strftime('%Y-%m-%d %H:%M:%S'))
        if other_user.is_online and timezone.now() - other_user.last_seen > timezone.timedelta(minutes=42):
            other_user.is_online = False
            other_user.save()

    if not error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users}
    elif error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users, 'error': error}
    else:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users, 'success': success}
    return context

# can get rid of this?
def friendsGET(request):
    return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, None, None))	


def friendResponse(request, data):
    from_username = data.get('from_user')
    from_user = CustomUser.objects.filter(username=from_username).first()
    if not from_user:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Could not find the friend candidate", None), "self_profile": True})    
    action = data.get('action')

    if action == 'unblock':
        request.user.blocked_users.remove(from_user)
        request.user.save()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Unblocked " + from_user.username), "self_profile": True})

    friendship = Friendship.objects.filter(Q(to_user=request.user, from_user=from_user) | Q(to_user=from_user, from_user=request.user)).first()
    if not friendship:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Could not find the friendship", None), "self_profile": True})    

    if action == 'accept':
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Congratulations, you made a new friend!"), "self_profile": True})
    elif action == 'reject':
        friendship.delete()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friendship REJECTED!"), "self_profile": True})
    elif action == 'delete':
        friendship.delete()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friendship DELETED!"), "self_profile": True})


def friendsPOST(request):
    logger.debug('in friendsPOST')
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('request_type') == 'friendResponse':
            return friendResponse(request, data)
        else:
            return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, ve, "Unknown content type"), "self_profile": True})

    sent_form = AddFriendForm(request.POST)
    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, ve, None), "self_profile": True})
    friend_username = sent_form.cleaned_data['username']
    current_user = request.user
    friend_user = CustomUser.objects.filter(username=friend_username).first()
    if friend_user in current_user.blocked_users.all() or current_user in friend_user.blocked_users.all():
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You cannot add or request friendship with a blocked user", None), "self_profile": True})

    # check if they are trying to add themselves
    if request.user.username == friend_username:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Please do not add yourself", None), "self_profile": True})

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
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You are already friends", None), "self_profile": True})

    # check if friend_user matches an incoming invite, and if yes, update the status of that Friendship to ACCEPTED
    incoming_invite = in_invites.filter(from_user=friend_user)
    if incoming_invite.exists():
        incoming_invite.update(status=Friendship.ACCEPTED)
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Congratulations, you made a new friend!"), "self_profile": True})

    # check if they have already sent a request to the user in question
    if out_invites.filter(to_user=friend_user):
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You have already sent a request to this user", None), "self_profile": True})

    # add to friends
    new_friendship = Friendship(from_user=current_user, to_user=friend_user, status=Friendship.PENDING)
    new_friendship.save()

    return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friend request sent"), "self_profile": True})


def block_user(request):
    logger.debug('in block_user')
    sent_form = AddFriendForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, ve, None), "self_profile": True})

    blocked_username = sent_form.cleaned_data['username']
    blocked_user = CustomUser.objects.get(username=blocked_username)
    current_user = request.user
    logger.debug('tryna block: ' + blocked_username)

    if request.user.username == blocked_username:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Please do not block yourself", None), "self_profile": True})

    if blocked_user in current_user.blocked_users.all():
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You have already blocked " + blocked_username + "!", None), "self_profile": True})

    # Delete possible friendship between them
    friendships_to_delete = Friendship.objects.filter(Q(from_user=current_user, to_user=blocked_user) | Q(from_user=blocked_user, to_user=current_user))
    friendships_to_delete.delete()

    # Delete pending game invites
    game_instances_to_delete = GameInstance.objects.filter(Q(p1=current_user, p2=blocked_user) | Q(p2=blocked_user, p1=current_user), status='Pending')
    game_instances_to_delete.delete()

    # Add to blocked
    current_user.blocked_users.add(blocked_user)
    current_user.save()

    return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Blocked " + blocked_username + "!"), "self_profile": True})


def playContext(request, error, success):
    logger.debug('in playContext()')
    current_user = request.user
    form = GameRequestForm()
    title = 'Play'
    all_games = GameInstance.objects.filter(Q(p1=current_user) | Q(p2=current_user))
    logger.debug('num of all_games(): ' + str(all_games.count()))
    invites_sent = all_games.filter(p1=current_user, status='Pending')
    invites_received = all_games.filter(p2=current_user, status='Pending')
    logger.debug('num of invites_received(): ' + str(invites_received.count()))

    context = {
        'current_user': current_user,
        'form': form,
        'all_games': all_games,
        'invites_sent': invites_sent,
        'invites_received': invites_received
    }

    if error:
        context['error'] = error
    elif success:
        context['success'] = success
    return context

def playGET(request):
    current_user = request.user
    all_games = GameInstance.objects.filter(Q(p1=current_user) | Q(p2=current_user))
    active_game = all_games.filter(Q(p1=current_user) | Q(p2=current_user), status='Active').first()
    if active_game is not None:
        # render the game canvas with the active game
        # they should never be able to be active in more than one game
        logger.debug('the user has an active game going on')
        return render(request, 'user/play.html', playContext(request, None, "ACTIVE GAME GOING ON, SHOULD RENDER THE GAME!"))
    else: #we render a menu in which they can choose game and send an invite to an opponent / reply to requests
        # if they are not currently playing, show game invite creation / pending invites
        # if they ARE currently listed as a part of a game, show the game canvas
        return render(request, 'user/play.html', playContext(request, None, None))


def gameResponse(request, data):
    action = data.get('action')
    if action == 'nuke':
        GameInstance.objects.all().delete()
        return render(request, 'user/play.html', playContext(request, None, "All GameInstances deleted"))
    challenger = data.get('from_user')
    challenger_user = CustomUser.objects.filter(username=challenger).first()
    if not challenger_user:
        return render(request, 'user/play.html', playContext(request, "Error: game cancelled / user deleted", None))    
    game_instance = GameInstance.objects.filter(p1=challenger_user, p2=request.user).first()
    if action == 'accept':
        game_instance.status = 'Active'
        game_instance.save()
        context =  playContext(request, None, "Game accepted! (this should redirect to game and start it)")
        context['p1_username'] = game_instance.p1.username
        context['p2_username'] = game_instance.p2.username
        return render(request, 'pong/pong.html', context)
        # return render(request, 'user/play.html', playContext(request, None, "Game accepted! (this should redirect to game and start it)"))
    elif action == 'reject':
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game rejected"))
    elif action == 'cancel':
        game_instance = GameInstance.objects.filter(p1=request.user, p2=challenger_user).first()
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game cancelled"))

# TODO: why does this return friends html?
def playPOST(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('request_type') == 'gameResponse':
            return gameResponse(request, data)
        else:
            return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, ve, "Unknown content type"))

    current_user = request.user
    sent_form = GameRequestForm(request.POST)
    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    challenged_username = sent_form.cleaned_data['username']
    challenged_user = CustomUser.objects.filter(username=challenged_username).first()
    if challenged_user in current_user.blocked_users.all() or current_user in challenged_user.blocked_users.all():
        return render(request, 'user/play.html', playContext(request, "Blocked", None))

    # check if they are trying to add themselves
    if request.user.username == challenged_username:
        return render(request, 'user/play.html', playContext(request, "No single player mode...", None))

    # request already sent?
    all_pending_games = GameInstance.objects.filter(Q(p1=current_user) | Q(p2=current_user), status='Pending')
    prior_request = all_pending_games.filter(Q(p1=challenged_user) | Q(p2=challenged_user)).first()
    if prior_request is not None:
        return render(request, 'user/play.html', playContext(request, "You have already sent a game request to this user", None)) 

    new_game_instance = GameInstance(p1=current_user, p2=challenged_user, game=sent_form.cleaned_data['game_type'], status='Pending')
    new_game_instance.save()
    return render(request, 'user/play.html', playContext(request, None, "Game invite sent! Should we be redirected to game here?")) 
    