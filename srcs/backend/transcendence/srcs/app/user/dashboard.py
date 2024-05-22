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

def check_user_not_none(user):
    if user is None:
        return "Deleted User"
    else:
        return user.username

def get_pong_history(username:str, pong_games:QuerySet) -> dict:
    pong_history = {}
    if not pong_games:
        return pong_history
    for iter, game in enumerate(pong_games):
        entry = {}
        entry["game"] = game.game
        entry["date"] = game.updated_at
        p1_username = check_user_not_none(game.p1)
        p2_username = check_user_not_none(game.p2)

        if p1_username == username:
            entry["opponent"] = p2_username
            entry["opponent_score"] = game.p2_score
            entry["user_score"] = game.p1_score
        else:
            entry["opponent"] = p1_username
            entry["opponent_score"] = game.p1_score
            entry["user_score"] = game.p2_score
        entry["winner"] = check_user_not_none(game.winner)
        entry["is_tournament_game"] = game.tournament_match
        pong_history[iter] = entry
    logger.debug(pong_history)
    return pong_history


def get_pong_stats(user:CustomUser, pong_games:QuerySet) -> dict:
    """
     - calculate win rate
     - set longest rally ever
     - biggest win margin
     - games played
     - win_percent
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
            logger.debug(f"User is {user.username} and winner is {game.winner}")
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
    pong_stats['win_percent'] = round((wins / pong_stats["games_played"]) * 100, 2)
    pong_stats["tournament_games"] = len(pong_games.filter(tournament_match=True))
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
        p1_username = check_user_not_none(game.p1)
        p2_username = check_user_not_none(game.p2)

        if p1_username == username:
            entry["opponent"] = p2_username
        else:
            entry["opponent"] = p1_username
        entry["winner"] = check_user_not_none(game.winner)
        entry["turns_to_win"] = game.turns_to_win
        entry["is_tournament_game"] = game.tournament_match
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
    wins = 0
    least_moves_to_win = color_games[0].turns_to_win
    sum_moves_to_win = 0
    for game in color_games:
        if user == game.winner:
            wins += 1
            sum_moves_to_win += game.turns_to_win
            if game.turns_to_win < least_moves_to_win:
                least_moves_to_win = game.turns_to_win
    color_stats["wins"] = wins
    color_stats['win_percent'] = round((wins / color_stats["games_played"]) * 100, 2)
    color_stats["least_moves_to_win"] = least_moves_to_win
    if wins:
        color_stats["average_move_to_win"] = sum_moves_to_win / wins
    else:
        color_stats["average_move_to_win"] = 0
    color_stats["tournament_games"] = len(color_games.filter(tournament_match=True))
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
    pong_stats = get_pong_stats(user, all_pong_games)
    color_history = get_color_history(username, all_color_games)
    color_stats = get_color_stats(user, all_color_games)
    stats = {'pong': pong_stats, 'color': color_stats}
    history = {'pong': pong_history, 'color': color_history}
    return history, stats

def get_wl_ratio(user, game):
    """
    if no previous games, returns 1
    if no losses, returns wins to avoid division by 0
    otherwise, returns a ratio wins/losses
    """
    logger.debug('calculating ratio of user ' + user.username + ' for game ' + game)
    if game == 'Pong':
        all_games = PongGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    else:
        all_games = ColorGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    if all_games.first() is None:
        logger.debug('no prior games, assuming ratio of 1')
        return 1
    wins = 0
    losses = 0
    games = 0
    for game in all_games:
        games += 1
        if user == game.winner:
            wins += 1
        else:
            losses += 1
    if losses == 0:
        logger.debug('no prior losses, assuming ratio of WIN == ' + wins)
        return wins
    ratio = wins / losses
    logger.debug('calculated ratio of ' + ratio)
    return ratio