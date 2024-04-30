from app.models import CustomUser, GameInstance
import logging


logger = logging.getLogger(__name__)

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
    return all_games