from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import requests
from django.shortcuts import render
from app.models import CustomUser, GameInstance
from django.db.models import Q
from app.forms import PlayerAuthForm
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)

@csrf_exempt
def get_game_state(request):
    try:
        if request.method == 'POST':
            p1_username = request.POST.get('p1_username')
            p2_username = request.POST.get('p2_username')
            logger.debug(f"data: {p1_username}, {p2_username}")
            logger.debug(request.POST)
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def get_canvas(request):
    logger.debug('In get_canvas()')
    if request.method == 'GET':
        logger.debug('about to render!')
        return render(request, "pong/pong.html", {})


def authenticate_player(request):
    sent_form = PlayerAuthForm(request.POST)
    sent_form.is_valid()

    username = request.POST.get('username')
    game_id = request.POST.get('game_id')
    password = sent_form.cleaned_data['password']

    current_game = GameInstance.objects.get(pk=game_id)

    context = {
        'p1_username': current_game.p1.username,
        'p2_username': current_game.p2.username,
        'p1_user': current_game.p1,
        'p2_user': current_game.p2,
        'form': PlayerAuthForm,
        'current_game': current_game
    }

    user = authenticate(request, username=username, password=password)
    if user is not None:
        if current_game.p1 == user:
            current_game.p1auth = True
            current_game.save()
        elif current_game.p2 == user:
            current_game.p2auth = True
            current_game.save()
    else:
        if username == current_game.p1.username:
            context['p1error'] = 'Auth failed!'
        elif username == current_game.p2.username:
            context['p2error'] = 'Auth failed!'

    return render(request, "pong/pong.html", context)


def pong_context(request, data):
    p1_user = CustomUser.objects.filter(username=data.get('p1')).first()
    p2_user = CustomUser.objects.filter(username=data.get('p2')).first()

    current_game = GameInstance.objects.filter(p1=p1_user, p2=p2_user, status='Accepted').first()

    current_user = request.user
    context = {
        'p1_username': p1_user.username,
        'p2_username': p2_user.username,
        'p1_user': p1_user,
        'p2_user': p2_user,
        'form': PlayerAuthForm,
        'current_game': current_game
    }
    return context


def post_pong_canvas(request):
    logger.debug('In post_pong_canvas()')
    data = json.loads(request.body)
    if request.method == 'POST':
        logger.debug('about to render!')
        return render(request, "pong/pong.html", pong_context(request, data))