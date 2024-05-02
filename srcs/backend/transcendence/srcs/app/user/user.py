from app.forms import  GameRequestForm
from app.models import CustomUser, GameInstance
from django.core.exceptions import ValidationError
import logging
from django.shortcuts import render
from django.db.models import Q
import json
# from django.contrib.auth import authenticate
# from django.contrib.auth import get_user_model
# from django.http import JsonResponse
# from django.http import HttpResponseRedirect
# from django.utils import timezone
# import os
# from transcendence import settings


logger = logging.getLogger(__name__)


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
    if not game_instance:
        return render(request, 'user/play.html', playContext(request, None, "Game not found"))
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


def playPOST(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('request_type') == 'gameResponse':
            return gameResponse(request, data)
        else:
            return render(request, 'user/play.html', playContext(request, None, "Unknown request type"))

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
    