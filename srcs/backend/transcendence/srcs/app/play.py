from .forms import GameRequestForm, LocalGameForm, StartTournamentForm, TournamentInviteForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .models import CustomUser, GameInstance, Tournament
from django.core.exceptions import ValidationError
import logging
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import Q
import json
from django.utils import timezone
import os
from transcendence import settings

logger = logging.getLogger(__name__)

def playContext(request, error, success):
    logger.debug('in playContext()')
    current_user = request.user
    inviteform = GameRequestForm()
    playform = LocalGameForm()
    tournamentform = StartTournamentForm()
    tournamentinviteform = TournamentInviteForm()
    title = 'Play'
    all_games = GameInstance.objects.filter(Q(p1=current_user) | Q(p2=current_user))
    invites_sent = all_games.filter(p1=current_user, status='Pending')
    invites_received = all_games.filter(p2=current_user, status='Pending')
    active_game = all_games.filter(Q(p1=current_user) | Q(p2=current_user), status='Accepted').first()
    my_tournament = Tournament.objects.filter(creator=request.user, status='Pending').first()
    
    if my_tournament is not None:
        hosting_tournament = True
    else:
        hosting_tournament = False

    context = {
        'current_user': current_user,
        'inviteform': inviteform,
        'playform': playform,
        'all_games': all_games,
        'invites_sent': invites_sent,
        'invites_received': invites_received,
        'tournamentform': tournamentform,
        'hosting_tournament': hosting_tournament,
        'my_tournament': my_tournament,
        'tournamentinviteform': tournamentinviteform
    }

    if active_game is not None:
        context['active_game'] = active_game

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
        return render(request, 'user/play.html', playContext(request, None, "ACTIVE GAME GOING ON, SHOULD RENDER THE GAME!"))
    else: #we render a menu in which they can choose game and send an invite to an opponent / reply to requests
        # if they are not currently playing, show game invite creation / pending invites
        # if they ARE currently listed as a part of a game, show the game canvas
        return render(request, 'user/play.html', playContext(request, None, None))


def check_player_activity(game_instance):
    p1 = game_instance.p1
    p2 = game_instance.p2

    # check if p1 or p2 is already in a game that is accepted or active
    if GameInstance.objects.filter(Q(p1=p1) | Q(p2=p1), status='Accepted'):
        return False
    elif GameInstance.objects.filter(Q(p1=p1) | Q(p2=p1), status='Active'):
        return False
    elif GameInstance.objects.filter(Q(p1=p2) | Q(p2=p2), status='Accepted'):
        return False
    elif GameInstance.objects.filter(Q(p1=p2) | Q(p2=p2), status='Active'):
        return False
    return True


def gameResponse(request, data):
    action = data.get('action')
    if action == 'nuke':
        GameInstance.objects.all().delete()
        Tournament.objects.all().delete()
        return render(request, 'user/play.html', playContext(request, None, "All GameInstances & Tournaments deleted"))
    challenger = data.get('from_user')
    challenger_user = CustomUser.objects.filter(username=challenger).first()
    if not challenger_user:
        return render(request, 'user/play.html', playContext(request, "Error: game cancelled / user deleted", None))    
    game_instance = GameInstance.objects.filter(p1=challenger_user, p2=request.user).first()
    if action == 'accept':
        if check_player_activity(game_instance) != True:
            return render(request, 'user/play.html', playContext(request, "Busy player, try again later", None))
        game_instance.status = 'Accepted'
        game_instance.save()
        return render(request, 'user/play.html', playContext(request, None, "Game accepted!"))
    elif action == 'reject':
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game rejected"))
    elif action == 'cancel':
        game_instance = GameInstance.objects.filter(p1=request.user, p2=challenger_user).first()
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game cancelled"))


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


def start_tournament(request):
    current_user = request.user
    sent_form = StartTournamentForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    game_type = sent_form.cleaned_data['game_type']
    logger.debug('user ' + current_user.username + ' started ' + game_type + ' tournament!')
    
    new_tournament = Tournament(creator=current_user, game=game_type, status='Pending')
    new_tournament.save()

    return render(request, 'user/play.html', playContext(request, None, 'Tournament created!'))


def tournament_invite(request):
    current_user = request.user
    sent_form = TournamentInviteForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    invited_username = sent_form.cleaned_data["username"]
    invited_user = CustomUser.objects.get(username=invited_username)

    if invited_user is None:
        return render(request, 'user/play.html', playContext(request, 'User not found', None))
    if invited_user == current_user:
        return render(request, 'user/play.html', playContext(request, 'Please do not invite yourself', None))


    return render(request, 'user/play.html', playContext(request, None, 'Invite sent!'))


def delete_tournament(request, data):
    logger.debug('In delete_tournament()')
    Tournament.objects.get(pk=data.get('tournament-id')).delete()
    return render(request, 'user/play.html', playContext(request, None, 'Tournament cancelled!'))


def tournament_buttons(request):
    logger.debug('In torunament_buttons()')
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('action') == 'nuke':
            return delete_tournament(request, data)
        # else:
        #     return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, ve, "Unknown content type"))

    return render(request, 'user/play.html', playContext(request, 'error in tournament_buttons()???', None))


def tournament_forms(request):
    formname = request.POST.get('formname')
    logger.debug('In start_tournament() received form: ' + formname)
    if formname == 'startTournamentForm':
        return start_tournament(request)
    elif formname == 'tournamentInviteForm':
        return tournament_invite(request)