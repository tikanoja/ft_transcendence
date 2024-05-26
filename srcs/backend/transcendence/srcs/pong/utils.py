from app.models import CustomUser, PongGameInstance, GameInstance, ColorGameInstance
from app.play import update_tournament
from django.http import JsonResponse
from app.forms import PlayerAuthForm
import logging


logger = logging.getLogger(__name__)


def save_cw_game_state(request):
	game_id = request.POST.get('game_id')
	game_instance = ColorGameInstance.objects.filter(pk=game_id).first()
	if game_instance is None:
		return JsonResponse({'message': 'Matching game instance not found'}, status=404)

	p1 = game_instance.p1
	p2 = game_instance.p2
	if not p1:
			return JsonResponse({'message': 'player 1 not found'}, status=404)
	elif not p2:
			return JsonResponse({'message': 'player 2 not found'}, status=404)

	game_instance.turns_to_win = request.POST.get("longest_rally")
	p1_score = request.POST.get("p1_score")
	p2_score = request.POST.get("p2_score")
	game_instance.p1_score = p1_score
	game_instance.p2_score = p2_score
	game_instance.status = 'Finished'
	if p1_score > p2_score:
			game_instance.winner = p1
	else:
			game_instance.winner = p2
	game_instance.save()
	if game_instance.tournament_match is True:
		update_tournament(game_instance)
	return JsonResponse({'message': 'Game data saved successfully!'}, status=200)


def save_pong_game_state(request) -> JsonResponse:
	"""
		Data format from pong_c:
		data_to_send = {
			"game" : "Pong",
			"p1_username": "placeholder",
			"p1_score": f"{p1_score}",
			"p2_username": "placeholder2",
			"p2_score": f"{p2_score}",
			"longest_rally": f"{rally}"
		}
	"""

	game_id = request.POST.get('game_id')
	game_instance = PongGameInstance.objects.filter(pk=game_id).first()
	if game_instance is None:
		return JsonResponse({'message': 'Matching game instance not found'}, status=404)

	p1 = game_instance.p1
	p2 = game_instance.p2
	if not p1:
			return JsonResponse({'message': 'player 1 not found'}, status=404)
	if not p2:
			return JsonResponse({'message': 'player 2 not found'}, status=404)

	game_instance.longest_rally_hits = request.POST.get("longest_rally")
	p1_score = request.POST.get("p1_score")
	p2_score = request.POST.get("p2_score")
	game_instance.p1_score = p1_score
	game_instance.p2_score = p2_score
	game_instance.status = 'Finished'
	if p1_score > p2_score:
			game_instance.winner = p1
	else:
			game_instance.winner = p2
	game_instance.save()
	if game_instance.tournament_match is True:
		update_tournament(game_instance)
	return JsonResponse({'message': 'Game data saved successfully!'}, status=200)
	

def game_exists(data):
    p1 = data.get('p1')
    p2 = data.get('p2')
    p1_user = CustomUser.objects.filter(username=p1).first()
    p2_user = CustomUser.objects.filter(username=p2).first()
    if p1_user is None or p2_user is None:
        return False
    current_game = GameInstance.objects.filter(p1=p1_user, p2=p2_user, status='Accepted').first()
    if current_game is None:
        return False
    return True


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
