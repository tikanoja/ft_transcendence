from .forms import GameRequestForm, LocalGameForm, StartTournamentForm, TournamentInviteForm, TournamentJoinForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .models import CustomUser, GameInstance, Tournament, Participant, Match, PongGameInstance, ColorGameInstance, PongGameInstance, ColorGameInstance
from django.core.exceptions import ValidationError
import logging
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import Q
import json
from django.utils import timezone
import os
from transcendence import settings

logger = logging.getLogger(__name__)

def playContext(request, error, success):
    logger.debug('in playContext()')
    current_user = request.user
    inviteform = GameRequestForm()
    playform = LocalGameForm()
    tournamentform = StartTournamentForm()
    tournamentinviteform = TournamentInviteForm()
    tournamentjoinform = TournamentJoinForm()

    title = 'Play'
    all_games = GameInstance.objects.filter(Q(p1=current_user) | Q(p2=current_user))
    invites_sent = all_games.filter(p1=current_user, status='Pending')
    invites_received = all_games.filter(p2=current_user, status='Pending')
    active_game = all_games.filter(Q(p1=current_user) | Q(p2=current_user), status='Accepted').first()
    my_tournament = Tournament.objects.filter(creator=request.user, status='Pending').first()
    tournament_in = Tournament.objects.filter(Q(status='Pending'), participants=current_user).first()
    tournament_in_participants = Participant.objects.filter(tournament=tournament_in)
    my_participant = tournament_in_participants.filter(user=current_user).first()
    in_active_tournament = False

    if my_tournament is None or my_tournament.participants is None:
        my_tournament_count = 0
    else:
        my_tournament_count = my_tournament.participants.filter(participant__status=Participant.ACCEPTED).count()

    if my_tournament is not None:
        hosting_tournament = True
    else:
        hosting_tournament = False

    if tournament_in is not None:
        participating_in_tournament = True
    else:
        participating_in_tournament = False

    tournament = Tournament.objects.filter(status='Active', participants=current_user).first()
    if tournament is not None:
        in_active_tournament = True
        matches = Match.objects.filter(tournament=tournament)
        levels = tournament.get_highest_level()
    else:
        in_active_tournament = False

    context = {
        'current_user': current_user,
        'inviteform': inviteform,
        'playform': playform,
        'all_games': all_games,
        'invites_sent': invites_sent,
        'invites_received': invites_received,
        'tournamentform': tournamentform,
        'hosting_tournament': hosting_tournament,
        'my_tournament': my_tournament,
        'tournamentinviteform': tournamentinviteform,
        'participating_in_tournament': participating_in_tournament,
        'tournament_in': tournament_in,
        'tournament_in_participants': tournament_in_participants,
        'my_participant': my_participant,
        'tournamentjoinform': tournamentjoinform,
        'my_tournament_count': my_tournament_count,
        'in_active_tournament': in_active_tournament,
    }

    if active_game is not None:
        context['active_game'] = active_game
    if in_active_tournament is True:
        context['matches'] = matches
        context['levels'] = levels
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
        return render(request, 'user/play.html', playContext(request, None, "ACTIVE GAME GOING ON, SHOULD RENDER THE GAME!"))
    else: #we render a menu in which they can choose game and send an invite to an opponent / reply to requests
        # if they are not currently playing, show game invite creation / pending invites
        # if they ARE currently listed as a part of a game, show the game canvas
        return render(request, 'user/play.html', playContext(request, None, None))


def check_player_activity(game_instance):
    p1 = game_instance.p1
    p2 = game_instance.p2

    # check if p1 or p2 is already in a game that is accepted or active
    if GameInstance.objects.filter(Q(p1=p1) | Q(p2=p1), status='Accepted'):
        return False
    elif GameInstance.objects.filter(Q(p1=p1) | Q(p2=p1), status='Active'):
        return False
    elif GameInstance.objects.filter(Q(p1=p2) | Q(p2=p2), status='Accepted'):
        return False
    elif GameInstance.objects.filter(Q(p1=p2) | Q(p2=p2), status='Active'):
        return False
    return True


def gameResponse(request, data):
    action = data.get('action')
    if action == 'nuke':
        GameInstance.objects.all().delete()
        Tournament.objects.all().delete()
        return render(request, 'user/play.html', playContext(request, None, "All GameInstances & Tournaments deleted"))
    challenger = data.get('from_user')
    challenger_user = CustomUser.objects.filter(username=challenger).first()
    if not challenger_user:
        return render(request, 'user/play.html', playContext(request, "Error: game cancelled / user deleted", None))
    game_instance = GameInstance.objects.filter(p1=challenger_user, p2=request.user, status='Pending').first()
    if game_instance is None:
        return render(request, 'user/play.html', playContext(request, "Could not find game", None))
    if action == 'accept':
        if check_player_activity(game_instance) != True:
            return render(request, 'user/play.html', playContext(request, "Busy player, try again later", None))
        game_instance.status = 'Accepted'
        game_instance.save()
        return render(request, 'user/play.html', playContext(request, None, "Game accepted!"))
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
            return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, ve, "Unknown content type"))

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

    game=sent_form.cleaned_data['game_type']
    if game == 'Pong':
        new_game_instance = PongGameInstance(p1=current_user, p2=challenged_user, game=game, status='Pending')
    else:
        new_game_instance = ColorGameInstance(p1=current_user, p2=challenged_user, game=game, status='Pending')
    new_game_instance.save()
    # CHAT MODULE let challenged user know that they have been challenged
    return render(request, 'user/play.html', playContext(request, None, "Game invite sent!")) 


def start_tournament(request):
    current_user = request.user
    sent_form = StartTournamentForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    # Check if the user is a participant in a tournament with a status of 'Pending' or 'Active'
    # if yes, show error 'Already registered to a tournament'

    game_type = sent_form.cleaned_data['game_type']
    alias = sent_form.cleaned_data['alias']
    logger.debug('user ' + current_user.username + ' started ' + game_type + ' tournament!')
    new_tournament = Tournament(creator=current_user, game=game_type, status='Pending')
    new_tournament.save()
    Participant.objects.create(user=current_user, tournament=new_tournament, alias=alias, status='Accepted')

    return render(request, 'user/play.html', playContext(request, None, 'Tournament created!'))


def tournament_join(request):
    logger.debug('in tournament_join()')
    current_user = request.user
    sent_form = TournamentJoinForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    alias = sent_form.cleaned_data["alias"]
    participant_id = request.POST.get('participant_id')
    participant = Participant.objects.get(pk=participant_id)

    if participant is None:
        return render(request, 'user/play.html', playContext(request, 'Participant instance not found', None))
 
    # change the status of the participant instance to 'Accepted'
    Participant.objects.filter(pk=participant_id).update(status='Accepted')
    Participant.objects.filter(pk=participant_id).update(alias=alias)

    return render(request, 'user/play.html', playContext(request, None, 'Joined tournament!'))


def tournament_invite(request):
    current_user = request.user
    sent_form = TournamentInviteForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    invited_username = sent_form.cleaned_data["username"]
    invited_user = CustomUser.objects.get(username=invited_username)

    if invited_user is None:
        return render(request, 'user/play.html', playContext(request, 'User not found', None))
    if invited_user == current_user:
        return render(request, 'user/play.html', playContext(request, 'Please do not invite yourself', None))

    tournament = Tournament.objects.get(creator=current_user)
    if tournament is None:
        return render(request, 'user/play.html', playContext(request, 'Could not find tournament', None))
    
    # if the invited_user is already in the tournament return error
    if Participant.objects.filter(user=invited_user, tournament=tournament).exists():
        return render(request, 'user/play.html', playContext(request, 'You have already invited that user', None))
    # add the invited_user to the tournament
    Participant.objects.create(user=invited_user, tournament=tournament, status='Pending')
    # CHAT MODULE msg to invited_user to inform that they have been invited to a tournament
    return render(request, 'user/play.html', playContext(request, None, 'Invite sent!'))


def delete_tournament(request, data):
    logger.debug('In delete_tournament()')
    Tournament.objects.get(pk=data.get('tournament-id')).delete()
    return render(request, 'user/play.html', playContext(request, None, 'Tournament cancelled!'))


def tournament_reject(request, data):
    logger.debug('In tournament_reject()')
    Participant.objects.get(pk=data.get('participant_id')).delete()
    return render(request, 'user/play.html', playContext(request, None, 'Rejected tournament invite!'))


def tournament_leave(request, data):
    logger.debug('In tournament_leave()')
    Participant.objects.get(pk=data.get('participant_id')).delete()
    return render(request, 'user/play.html', playContext(request, None, 'Left tournament!'))


def update_tournament(game_instance):
    logger.debug('in update_tournament')
    match = Match.objects.filter(game_instance=game_instance).first()
    if Match is None:
        logger.debug('could not find match! :(')
    else:
        logger.debug('Match found!')

    tournament = match.tournament
    if Tournament is None:
        logger.debug('could not find tournament! : (')
    else:
        logger.debug('tournament found!')
    
    if match.is_last_of_level() is True:
        logger.debug('Last match of level finished, checking if more levels in tournament...')
        if match.level < tournament.get_highest_level():
            logger.debug('There are higher levels! Filling in TBD bracket of level ' + str(match.level + 1))
            match.status = Match.FINISHED
            match.save()
            # Get the winners of matches with match.level (there will be 2 or 4)
            winners = Match.objects.filter(tournament=tournament, level=match.level, status=Match.FINISHED).values_list('game_instance__winner', flat=True)
            # Get the next level matches
            next_level_matches = Match.objects.filter(tournament=tournament, level=match.level + 1, status=Match.TBD)
            # Fill in match.level + 1 games p1 and p2 with those users (there will be 1 or 2 games to fill in)
            # and change the status of the newly filled in games to 'Scheduled'
            for i, next_level_match in enumerate(next_level_matches):
                if i * 2 < len(winners):
                    p1_user = CustomUser.objects.get(id=winners[i * 2])
                    p2_user = CustomUser.objects.get(id=winners[i * 2 + 1])
                    next_level_match.game_instance.p1 = p1_user
                    next_level_match.game_instance.p2 = p2_user
                    next_level_match.game_instance.status = 'Accepted'
                    next_level_match.game_instance.save()
                    next_level_match.status = Match.SCHEDULED
                    next_level_match.save()
                    logger.debug(f'Scheduled a game: {p1_user.username} vs {p2_user.username}!')
                    # CHAT MODULE let player know in chat that they have a new game
        else:
            logger.debug('No more levels in tournament, finishing tournament!')
            # CHAT MODULE announce tournament winner
            match.status = Match.FINISHED
            match.save()
            tournament.status = Tournament.FINISHED
            tournament.save()
    else:
        logger.debug('There are still matches remaining on this level of the tournament')
        # CHAT MODULE let player know that we are waiting for games to finish
        match.status = Match.FINISHED
        match.save()

    
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
    logger.debug('calculated ratio of ' + str(ratio))
    return ratio


def generate_brackets(tournament, accepted_participants):
    logger.debug('generating tournament brackets...')
    if tournament.status != Tournament.ACTIVE:
        raise ValueError("Tournament must be active to generate brackets!")
    num_participants = accepted_participants.count()
    total_games = num_participants - 1
    game_type = tournament.game

    participants_with_ratios = []
    for participant in accepted_participants:
        user = participant.user
        ratio = get_wl_ratio(user, game_type)
        participants_with_ratios.append((participant, ratio))

    logger.debug('\nbefore sorting')
    for participant, ratio in participants_with_ratios:
        logger.debug(f"{participant.user.username}: {ratio}")

    # Sort participants based on their win/loss ratio
    sorted_participants = sorted(participants_with_ratios, key=lambda x: x[1])

    logger.debug('\nafter sorting')
    for participant, ratio in sorted_participants:
        logger.debug(f"{participant.user.username}: {ratio}")

    # Extract just the sorted participants (without the ratios)
    sorted_participant_objects = [item[0] for item in sorted_participants]

    logger.debug("\nUsernames in sorted order:")
    for participant in sorted_participant_objects:
        logger.debug(participant.user.username)

    # creating the first round of games
    for i in range(0, num_participants, 2):
        game_instance = GameInstance.objects.create(
            p1=sorted_participant_objects[i].user,
            p2=sorted_participant_objects[i+1].user,
            status='Accepted',
            tournament_match=True,
            game=tournament.game,
        )
        match = Match.objects.create(
            tournament=tournament,
            game_instance=game_instance,
            status='Scheduled',
            level=1
        )
    
    # creating 4 player final 
    if num_participants == 4:
        game_instance = GameInstance.objects.create(
            p1=None,
            p2=None,
            status='Accepted',
            tournament_match=True,
            game=tournament.game,
        )
        match = Match.objects.create(
            tournament=tournament,
            game_instance=game_instance,
            status='TBD',
            level=2
        )
        logger.debug('making one final game (4p)')
    
    # creating 8 player semifinals and final
    if num_participants == 8:
        logger.debug('In 8 player follow up creation')
        for _ in range(2): # Creates semifinals
            game_instance = GameInstance.objects.create(
                p1=None,
                p2=None,
                status='Accepted',
                tournament_match=True,
                game=tournament.game,
            )
            match = Match.objects.create(
                tournament=tournament,
                game_instance=game_instance,
                status='TBD',
                level=2
            )
            logger.debug('created a semifinal (8p)')
        # Final
        game_instance = GameInstance.objects.create(
            p1=None,
            p2=None,
            status='Accepted',
            tournament_match=True,
            game=tournament.game,
        )
        match = Match.objects.create(
            tournament=tournament,
            game_instance=game_instance,
            status='TBD',
            level=3
        )
        logger.debug('created the final (8p)')


def tournament_start(request, data):
    current_user = request.user
    # Get tournament
    tournament = Tournament.objects.filter(creator=current_user).first()
    if tournament is None:
        return render(request, 'user/play.html', playContext(request, 'Could not find tournament instance...', None))

    # Get participants
    participants = Participant.objects.filter(tournament=tournament)
    accepted_participants = participants.filter(status='Accepted')

    # Check that we still have 4 - 16 players accepted
    if accepted_participants.count() != 4 and accepted_participants.count() != 8:
        return render(request, 'user/play.html', playContext(request, 'Wrong amount of participants', None))

    # Delete pending participants (those who did not accept the inv before the creator started the tournament)
    pending_participants = participants.filter(status='Pending')
    pending_participants.delete()

    # change tournament status
    tournament.status = 'Active'
    tournament.save()

    # generate brackets
    try:
        generate_brackets(tournament, accepted_participants)
    except ValueError as e:
        return render(request, 'user/play.html', playContext(request, str(e), None))
    # CHAT MODULE announce tournament start
    return render(request, 'user/play.html', playContext(request, None, 'Tournament started!'))


def tournament_buttons(request):
    logger.debug('In torunament_buttons()')
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('action') == 'nuke':
            return delete_tournament(request, data)
        if data.get('action') == 'rejectTournamentInvite':
            return tournament_reject(request, data)
        if data.get('action') == 'leaveTournament':
            return tournament_leave(request, data)
        if data.get('action') == 'startTournament':
            return tournament_start(request, data)
        # else:
        #     return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, ve, "Unknown content type"))

    return render(request, 'user/play.html', playContext(request, 'error in tournament_buttons()???', None))


def tournament_forms(request):
    formname = request.POST.get('formname')
    logger.debug('In tournament_forms() received form: ' + formname)
    if formname == 'startTournamentForm':
        return start_tournament(request)
    elif formname == 'tournamentInviteForm':
        return tournament_invite(request)
    elif formname == 'tournamentJoinForm':
        return tournament_join(request)