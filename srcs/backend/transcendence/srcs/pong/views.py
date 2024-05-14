from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import requests
from django.shortcuts import render
from . import utils
from app.models import PongGameInstance, CustomUser, GameInstance
from app.user import dashboard
from app.play import playContext
from django.db.models import Q
from app.forms import PlayerAuthForm
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


@csrf_exempt
def cli_dashboard(request, username):
     try:
        if request.method == 'GET':
            user = CustomUser.objects.filter(username=username).first()
            pong_games = PongGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
            resource = dashboard.get_stats_for_cli(user, pong_games)
            return JsonResponse({'pong': resource}, status=200)
        else:
            return JsonResponse({"error": "method not allowed, try GET"}, status=405)
     except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def save_game_state(request):
    logger.debug('in save_game_state')
    try:
        logger.debug('checking all game instances for pong')
        if request.method == 'POST':
            game_type = request.POST.get('game')
            if game_type == 'Pong':
                response = utils.save_pong_game_state(request)
            else:
                response = JsonResponse({'message': 'Invalid game type!'}, status=400)
        elif request.method == 'GET':
            response = JsonResponse({'message': 'Hi from Django GET!'}, status=200)
        return response
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def validate_match(request):
    try:
        if request.method == 'POST':
            p1_username = request.POST.get('p1_username')
            p2_username = request.POST.get('p2_username')
            logger.debug(f"data from validate user: {p1_username}, {p2_username}")
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def authenticate_player(request):
    sent_form = PlayerAuthForm(request.POST)
    sent_form.is_valid()

    username = request.POST.get('username')
    game_id = request.POST.get('game_id')
    password = sent_form.cleaned_data['password']

    current_game = GameInstance.objects.get(pk=game_id)
    game_type = current_game.game

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

    if game_type == 'Pong':
        return render(request, "pong/pong.html", context)
    elif game_type == 'Color':
        return render(request, "pong/colorwar.html", context)
    else:
        return render(request, "pong/play.html", playContext(request, 'Unknown game type', None))


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
        'current_game': current_game,
        'current_user':  current_user.username
    }
    return context


def post_pong_canvas(request):
    logger.debug('In post_pong_canvas()')
    data = json.loads(request.body)
    if request.method == 'POST':
        logger.debug('about to render!')
        return render(request, "pong/pong.html", pong_context(request, data))

def post_cw_canvas(request):
    logger.debug('In post_cw_canvas()')
    data = json.loads(request.body)
    if request.method == 'POST':
        logger.debug('about to render!')
        return render(request, "pong/colorwar.html", pong_context(request, data))
