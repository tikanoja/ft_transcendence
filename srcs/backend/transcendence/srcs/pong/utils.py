from app.models import GameInstance, CustomUser, PongGameInstance
from django.http import JsonResponse
import logging


logger = logging.getLogger(__name__)


"""
	Data format from pong_c:
	data_to_send = {"game" : "Pong",
		"p1_username": "placeholder",
		"p1_score": f"{p1_score}",
		"p2_username": "placeholder2",
		"p2_score": f"{p2_score}",
		"longest_rally": f"{rally}"
	}
"""
def save_pong_game_state(request) -> JsonResponse:
	logger.debug('in save_pong_game_state')
	p1_username = request.POST.get('p1_username')
	p2_username = request.POST.get('p2_username')
	p1 = CustomUser.objects.filter(username=p1_username).first()
	p2 = CustomUser.objects.filter(username=p2_username).first()
	if not p1:
			logger.debug('P1 not found')
			return JsonResponse({'message': 'player 1 not found'}, status=404)
	if not p2:
			logger.debug('P2 not found')
			return JsonResponse({'message': 'player 2 not found'}, status=404)
	game_instance = PongGameInstance.objects.filter(p1=p1, p2=p2).first()
	if not game_instance:
			logger.debug('Game instance not found not found')
			return JsonResponse({'message': 'Matching game instance not found'}, status=404)
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
	logger.debug(game_instance)
	return JsonResponse({'message': 'Game data saved successfully!'}, status=200)