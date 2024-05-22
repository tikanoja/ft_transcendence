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
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@csrf_exempt
def cli_dashboard(request, username):
     try:
        print(request, username)
        if request.method == 'GET':
            user = CustomUser.objects.filter(username=username).first()
            pong_games = PongGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
            resource = dashboard.get_stats_for_cli(user, pong_games)
            print(resource)
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
            logger.debug('game type: ' + game_type)
            if game_type == 'Pong':
                response = utils.save_pong_game_state(request)
            elif game_type == 'Color':
                response = utils.save_cw_game_state(request)
            else:
                response = JsonResponse({'message': 'Invalid game type!'}, status=400)
            return response
        else:
            response = JsonResponse({'message': 'Method not allowed. Only POST'}, status=405)
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)

"""
TODO:What is the purpose of this?
"""
@csrf_exempt
def validate_match(request):
    try:
        if request.method == 'POST':
            p1_username = request.POST.get('p1_username')
            p2_username = request.POST.get('p2_username')
            game_id = request.POST.get('game_id')
            logger.debug(f"data from validate user: {p1_username}, {p2_username}, {game_id}")
            return JsonResponse({'message': 'Hi from Django POST!'})
        elif request.method == 'GET':
            return JsonResponse({'message': 'Hi from Django GET!'})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def authenticate_player(request):
    try:
        if request.method == "POST":
            sent_form = PlayerAuthForm(request.POST)
            sent_form.is_valid()

            username = request.POST.get('username')
            game_id = request.POST.get('game_id')
            password = sent_form.cleaned_data['password']

            current_game = GameInstance.objects.filter(pk=game_id).first()
            if current_game is None:
                return render(request, "pong/play.html", playContext(request, 'Could not find game instance', None))
            
            game_type = current_game.game
            current_user = request.user
            context = {
                'p1_username': current_game.p1.username,
                'p2_username': current_game.p2.username,
                'p1_user': current_game.p1,
                'p2_user': current_game.p2,
                'form': PlayerAuthForm,
                'current_game': current_game,
                'current_user': current_user,
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
        else:
            response = JsonResponse({'message': 'Method not allowed. Only POST'}, status=405)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def post_pong_canvas(request):
    try:
        logger.debug('In post_pong_canvas()')
        if request.method == 'POST':
            data = json.loads(request.body)
            if utils.game_exists(data) is False:
                return render(request, 'user/play.html', playContext(request, "Game not found!", None))
            return render(request, "pong/pong.html", utils.pong_context(request, data))
        else:
            return render(request, "pong/nogame.html", {'current_user': request.user})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def post_cw_canvas(request):
    try:
        logger.debug('In post_cw_canvas()')
        if request.method == 'POST':
            data = json.loads(request.body)
            if utils.game_exists(data) is False:
                return render(request, 'user/play.html', playContext(request, "Game not found!", None))
            return render(request, "pong/colorwar.html", utils.pong_context(request, data))
        else:
            return render(request, "pong/nogame.html", {'current_user': request.user})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    

def notfound(request):
    try:
        logger.debug('in notfound()')
        if request.method == 'GET':
            # check for current_user
            context = {}
            context["current_user"] = request.user
            return render(request, '404.html', context)
        else:
            return JsonResponse({'error': "method not allowed. please use GET"}, , status=405)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)
