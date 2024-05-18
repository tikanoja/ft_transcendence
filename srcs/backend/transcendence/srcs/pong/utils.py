from app.models import CustomUser, PongGameInstance, Match, Tournament, GameInstance, ColorGameInstance
from app.play import update_tournament
from django.http import JsonResponse
import logging


logger = logging.getLogger(__name__)


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

def save_cw_game_state(request):
	logger.debug('in save_cw_game_state()')
	logger.debug(request.POST)

	game_id = request.POST.get('game_id')
	game_instance = ColorGameInstance.objects.get(pk=game_id)
	if game_instance is None:
		return JsonResponse({'message': 'Matching game instance not found'}, status=404)

	p1 = game_instance.p1
	p2 = game_instance.p2
	if not p1:
			logger.debug('P1 not found')
			return JsonResponse({'message': 'player 1 not found'}, status=404)
	elif not p2:
			logger.debug('P2 not found')
			return JsonResponse({'message': 'player 2 not found'}, status=404)
	p1_username = p1.username
	p2_username = p2.username

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
	logger.debug('COLOR game id ' + str(game_instance.id) + ' | p1 ' + game_instance.p1.username + ' scored ' + game_instance.p1_score + ' | p2 ' + game_instance.p2.username + ' scored ' + game_instance.p2_score + ' | winner: ' + game_instance.winner.username)
	return JsonResponse({'message': 'Game data saved successfully!'}, status=200)


def save_pong_game_state(request) -> JsonResponse:
	logger.debug('in save_pong_game_state')
	logger.debug(request.POST)

	game_id = request.POST.get('game_id')
	game_instance = PongGameInstance.objects.get(pk=game_id)
	if game_instance is None:
		return JsonResponse({'message': 'Matching game instance not found'}, status=404)

	p1 = game_instance.p1
	p2 = game_instance.p2
	if not p1:
			logger.debug('P1 not found')
			return JsonResponse({'message': 'player 1 not found'}, status=404)
	if not p2:
			logger.debug('P2 not found')
			return JsonResponse({'message': 'player 2 not found'}, status=404)
	p1_username = p1.username
	p2_username = p2.username

	game_instance.longest_rally_hits = request.POST.get("longest_rally")
	p1_score = request.POST.get("p1_score")
	p2_score = request.POST.get("p2_score")
	game_instance.p1_score = p1_score
	game_instance.p2_score = p2_score
	logger.debug(p1_username + ' scored ' + p1_score + ' and ' + p2_username + ' scored ' + p2_score)
	game_instance.status = 'Finished'
	if p1_score > p2_score:
			game_instance.winner = p1
	else:
			game_instance.winner = p2
	game_instance.save()
	if game_instance.tournament_match is True:
		update_tournament(game_instance)
	logger.debug('PONG game id ' + str(game_instance.id) + ' | p1 ' + game_instance.p1.username + ' scored ' + game_instance.p1_score + ' | p2 ' + game_instance.p2.username + ' scored ' + game_instance.p2_score + ' | winner: ' + game_instance.winner.username)
	return JsonResponse({'message': 'Game data saved successfully!'}, status=200)
	
