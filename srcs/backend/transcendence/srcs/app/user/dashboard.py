from app.models import CustomUser, GameInstance, PongGameInstance, ColorGameInstance
from django.db.models import Q, QuerySet
import logging


logger = logging.getLogger(__name__)

def get_stats_for_cli(user:CustomUser, pong_games:QuerySet) -> dict:
    """
    - games played
    - games won
    """
    pong_stats = {}
    pong_stats["games_played"] = len(pong_games)
    won_games = pong_games.filter(winner=user)
    pong_stats["wins"] = len(won_games)
    return pong_stats


def get_pong_history(username:str, pong_games:QuerySet) -> dict:
    pong_history = {}
    if not pong_games:
        return pong_history
    for iter, game in enumerate(pong_games):
        entry = {}
        entry["game"] = game.game
        entry["date"] = game.updated_at
        if game.p1.username == username:
            entry["opponent"] = game.p2
            entry["opponent_score"] = game.p2_score
            entry["user_score"] = game.p1_score
        else:
            entry["opponent"] = game.p1
            entry["opponent_score"] = game.p1_score
            entry["user_score"] = game.p2_score
        entry["winner"] = game.winner.username
        pong_history[iter] = entry
    logger.debug(pong_history)
    return pong_history


def get_pong_stats(user:CustomUser, pong_games:QuerySet) -> dict:
    """
     - calculate win rate
     - set longest rally ever
     - biggest win margin
     - games played
    """
    pong_stats = {}
    pong_stats["games_played"] = len(pong_games)
    if not pong_games:
        return pong_stats
    wins = 0
    largest_win_margin = 0
    largest_loss_margin = 0
    longest_rally = 0
    for game in pong_games:
        is_p1 = (game.p1 == user)
        margin = 0
        if user == game.winner:
            wins += 1
            if is_p1:
                margin = game.p1_score - game.p2_score
            else:
                margin = game.p2_score - game.p1_score
            if margin > largest_win_margin:
                largest_win_margin = margin
        else:
            if is_p1:
                margin = game.p2_score - game.p1_score
            else:
                margin = game.p1_score - game.p2_score
            if margin > largest_loss_margin:
                largest_win_margin = margin
        if game.longest_rally_hits > longest_rally:
            longest_rally = game.longest_rally_hits
    pong_stats["wins"] = wins
    pong_stats["largest_win_margin"] = largest_win_margin
    pong_stats['largest_loss_margin'] = largest_loss_margin
    pong_stats['longest_rally'] = longest_rally
    logger.debug(pong_stats)
    return pong_stats


def get_color_history(username:str, color_games:QuerySet) -> dict:
    color_history = {}
    if not color_games:
        return color_history
    for iter, game in enumerate(color_games):
        entry = {}
        entry["game"] = game.game
        entry["date"] = game.updated_at
        if game.p1.username == username:
            entry["opponent"] = game.p2
        else:
            entry["opponent"] = game.p1
        entry["winner"] = game.winner.username
        entry["turns_to_win"] = game.turns_to_win
        color_history[iter] = entry
    logger.debug(color_history)
    return color_history


def get_color_stats(user:CustomUser, color_games:QuerySet) -> dict:
    """
     - calculate win rate
     - least moves to win
     - games played
     - average moves to win
    """
    color_stats = {}
    color_stats["games_played"] = len(color_games)
    if not color_games:
        return color_stats
    wins = color_games[0].turns_to_win
    least_moves_to_win = 0
    sum_moves_to_win = 0
    for game in color_games:
        if user == game.winner:
            wins += 1
            sum_moves_to_win += game.turns_to_win
            if game.turns_to_win < least_moves_to_win:
                least_moves_to_win = game.turns_to_win
    color_stats["wins"] = wins
    color_stats["least_moves_to_win"] = least_moves_to_win
    if wins:
        color_stats["average_move_to_win"] = sum_moves_to_win / wins
    else:
        color_stats["average_move_to_win"] = 0
    logger.debug(color_stats)
    return color_stats


def get_game_history_and_stats(username:str) -> dict:
    logger.debug("in get game history")
    user = CustomUser.objects.get(username=username)
    all_pong_games = PongGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    logger.debug('all pong games: ')
    logger.debug(all_pong_games)
    all_color_games = ColorGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    pong_history = get_pong_history(username, all_pong_games)
    pong_stats = get_pong_stats(username, all_pong_games)
    color_history = get_color_history(username, all_color_games)
    color_stats = get_color_stats(user, all_color_games)
    stats = {'pong': pong_stats, 'color': color_stats}
    history = {'pong': pong_history, 'color': color_history}
    return history, stats

