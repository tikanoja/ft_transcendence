from .forms import GameRequestForm, LocalGameForm, StartTournamentForm, TournamentInviteForm, TournamentJoinForm
from .models import CustomUser, GameInstance, Tournament, Participant, Match, PongGameInstance, ColorGameInstance, PongGameInstance, ColorGameInstance
from django.core.exceptions import ValidationError
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
import json

import app.consumers

logger = logging.getLogger(__name__)

def playContext(request, error, success):
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
        'active': "play",
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
    if action == 'accept':
        game_instance = GameInstance.objects.filter(p1=challenger_user, p2=request.user, status='Pending').first()
        if game_instance is None:
            return render(request, 'user/play.html', playContext(request, "Could not find game", None))
        if check_player_activity(game_instance) != True:
            return render(request, 'user/play.html', playContext(request, "Busy player, try again later", None))
        game_instance.status = 'Accepted'
        game_instance.save()
        return render(request, 'user/play.html', playContext(request, None, "Game accepted!"))
    elif action == 'reject':
        game_instance = GameInstance.objects.filter(p1=challenger_user, p2=request.user, status='Pending').first()
        if game_instance is None:
            return render(request, 'user/play.html', playContext(request, "Could not find game", None))
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game rejected"))
    elif action == 'cancel':
        game_instance = GameInstance.objects.filter(p1=request.user, p2=challenger_user, status='Pending').first()
        if game_instance is None:
            return render(request, 'user/play.html', playContext(request, "Could not find game", None))
        game_instance.delete()
        return render(request, 'user/play.html', playContext(request, None, "Game cancelled"))


def playPOST(request):
    try: 
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            if data.get('request_type') == 'gameResponse':
                return gameResponse(request, data)
            else:
                return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, ve, "Unknown content type"))

        sent_form = GameRequestForm(request.POST)
        if not sent_form.is_valid():
                raise ValidationError("Form filled incorrectly")

        challenged_username: str    = sent_form.cleaned_data['username']
        challenged_user: CustomUser = CustomUser.objects.get(username=challenged_username)

        game = sent_form.cleaned_data["game_type"]
        as_user_challenge_user(request.user, challenged_user, game)

    # Realistically should have different dispatch for various different exceptions
    except ValidationError as e:
        error_message = e.message if hasattr(e, "message") else str(e)
        return render(request, 'user/play.html', playContext(request, error_message, None))

    return render(request, 'user/play.html', playContext(request, None, "Game invite sent!")) 


def as_user_challenge_user(user: CustomUser, challengee: CustomUser, game_name: str):
    # Check if participants have blocked each other
    if challengee in user.blocked_users.all() or user in challengee.blocked_users.all():
        raise ValidationError("You are blocked")
        #return render(request, 'user/play.html', playContext(request, "Blocked", None))

    # check if they are trying to add themselves
    if user.username == challengee.username:
        raise ValidationError("No single player mode...")

    # request already sent?
    all_pending_games = GameInstance.objects.filter(Q(p1=user) | Q(p2=user), status='Pending')
    prior_request = all_pending_games.filter(Q(p1=challengee) | Q(p2=challengee)).first()
    if prior_request is not None:
        raise ValidationError("You have already sent a game request to this user")

    new_game_instance = None
    match (game_name.lower()):
        case "pong":
            new_game_instance = PongGameInstance(p1=user, p2=challengee, game=game_name, status='Pending')
        case "color":
            new_game_instance = ColorGameInstance(p1=user, p2=challengee, game=game_name, status='Pending')
        case _:
            raise ValidationError("Invalid game type")

    new_game_instance.save()

    app.consumers.chat_system_message(challengee, "{name} has challenged you to a game of {game}".format(name = user.username, game = game_name))


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
    new_tournament = Tournament(creator=current_user, game=game_type, status='Pending')
    new_tournament.save()
    Participant.objects.create(user=current_user, tournament=new_tournament, alias=alias, status='Accepted')

    return render(request, 'user/play.html', playContext(request, None, 'Tournament created!'))


def tournament_join(request):
    current_user = request.user
    sent_form = TournamentJoinForm(request.POST)

    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/play.html', playContext(request, ve, None))
    
    alias = sent_form.cleaned_data["alias"]
    participant_id = request.POST.get('participant_id')
    participant = Participant.objects.filter(pk=participant_id).first()

    if participant is None:
        return render(request, 'user/play.html', playContext(request, 'Participant instance not found', None))

    # check if participant is hosting a pending tournament, cancel that if yes
    participant_user = participant.user
    hosting_tournament = Tournament.objects.filter(creator=participant_user, status='Pending').first()
    if hosting_tournament is not None:
        hosting_tournament.delete()

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
    invited_user = CustomUser.objects.filter(username=invited_username).first()

    if invited_user is None:
        return render(request, 'user/play.html', playContext(request, 'User not found', None))
    if invited_user == current_user:
        return render(request, 'user/play.html', playContext(request, 'Please do not invite yourself', None))
    if current_user in invited_user.blocked_users.all():
        return render(request, 'user/play.html', playContext(request, 'You cannot invite users who have blocked you.', None))

    tournament = Tournament.objects.filter(creator=current_user, status='Pending').first()
    if tournament is None:
        return render(request, 'user/play.html', playContext(request, 'Could not find tournament', None))
    
    # if the invited_user is already in the tournament return error
    if Participant.objects.filter(user=invited_user, tournament=tournament).exists():
        return render(request, 'user/play.html', playContext(request, 'You have already invited that user', None))
    # add the invited_user to the tournament
    Participant.objects.create(user=invited_user, tournament=tournament, status='Pending')

    app.consumers.chat_system_message(invited_user, "{name} has invited you to a tournament!".format(name = request.user.username))

    return render(request, 'user/play.html', playContext(request, None, 'Invite sent!'))


def delete_tournament(request, data):
    tournament = Tournament.objects.filter(pk=data.get('tournament-id')).first()
    if tournament is None:
        return render(request, 'user/play.html', playContext(request, 'Tournament instance not found!', None))
    tournament.delete()
    return render(request, 'user/play.html', playContext(request, None, 'Tournament cancelled!'))


def tournament_reject(request, data):
    participant = Participant.objects.filter(pk=data.get('participant_id')).first()
    if participant is None:
        return render(request, 'user/play.html', playContext(request, 'Participant instance not found.', None))
    participant.delete()
    return render(request, 'user/play.html', playContext(request, None, 'Rejected tournament invite!'))


def tournament_leave(request, data):
    participant = Participant.objects.filter(pk=data.get('participant_id')).first()
    if participant is None:
        return render(request, 'user/play.html', playContext(request, 'Participant instance not found.', None))
    tournament = participant.tournament
    if tournament.status != Tournament.PENDING:
        return render(request, 'user/play.html', playContext(request, 'Too late, tournament already started!', None))
    participant.delete()
    return render(request, 'user/play.html', playContext(request, None, 'Left tournament!'))


def update_tournament(game_instance):
    match = Match.objects.filter(game_instance=game_instance).first()

    tournament = match.tournament
    
    if match.is_last_of_level() is True:
        # Last match of level finished, checking if more levels in tournament...
        if match.level < tournament.get_highest_level():
            # There are higher levels! Filling in TBD bracket of level
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
                    # Scheduled a game
                    for matchup in [(p1_user, p2_user), (p2_user, p1_user)]:
                        app.consumers.chat_system_message(matchup[0], "Your next tournament match is against {name}!".format(name=matchup[1].username))

        else:
            # No more levels in tournament, finishing tournament!
            match.status = Match.FINISHED
            match.save()
            tournament.status = Tournament.FINISHED
            tournament.save()
            winner_username = match.game_instance.winner.username
            for p in Participant.objects.filter(tournament=tournament):
                app.consumers.chat_system_message(p.user, "Congratulations to {name} for winning the tournament!".format(name=winner_username))
    else:
        # There are still matches remaining on this level of the tournament
        match.status = Match.FINISHED
        match.save()
        winner = match.game_instance.winner
        app.consumers.chat_system_message(winner, "Matches are still ongoing, please wait for your next game.")

    
def get_wl_ratio(user, game):
    """
    if no previous games, returns 1
    if no losses, returns wins to avoid division by 0
    otherwise, returns a ratio wins/losses
    """
    if game == 'Pong':
        all_games = PongGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    else:
        all_games = ColorGameInstance.objects.filter(Q(p1=user) | Q(p2=user)).filter(status='Finished')
    if all_games.first() is None:
        # no prior games, assuming ratio of 1
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
        # no prior losses assume w/l ratio
        return wins
    ratio = wins / losses
    return ratio


def generate_brackets(tournament, accepted_participants):
    # logger.debug('generating tournament brackets...')
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

    # logger.debug('\nbefore sorting')
    # for participant, ratio in participants_with_ratios:
    #     logger.debug(f"{participant.user.username}: {ratio}")

    # Sort participants based on their win/loss ratio
    sorted_participants = sorted(participants_with_ratios, key=lambda x: x[1])

    # logger.debug('\nafter sorting')
    # for participant, ratio in sorted_participants:
    #     logger.debug(f"{participant.user.username}: {ratio}")

    # Extract just the sorted participants (without the ratios)
    sorted_participant_objects = [item[0] for item in sorted_participants]

    # logger.debug("\nUsernames in sorted order:")
    # for participant in sorted_participant_objects:
    #     logger.debug(participant.user.username)

    if game_type == 'Pong':
        game_instance_model = PongGameInstance
    else:
        game_instance_model = ColorGameInstance

    # creating the first round of games
    for i in range(0, num_participants, 2):
        game_instance = game_instance_model.objects.create(
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
        game_instance = game_instance_model.objects.create(
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
        # logger.debug('making one final game (4p)')
    
    # creating 8 player semifinals and final
    if num_participants == 8:
        # logger.debug('In 8 player follow up creation')
        for _ in range(2): # Creates semifinals
            game_instance = game_instance_model.objects.create(
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
            # logger.debug('created a semifinal (8p)')
        # Final
        game_instance = game_instance_model.objects.create(
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
        # logger.debug('created the final (8p)')


def tournament_start(request, data):
    current_user = request.user
    # Get tournament
    tournament = Tournament.objects.filter(creator=current_user, status=Tournament.PENDING).first()
    if tournament is None:
        return render(request, 'user/play.html', playContext(request, 'Could not find tournament instance...', None))

    # Get participants
    participants = Participant.objects.filter(tournament=tournament)
    accepted_participants = participants.filter(status='Accepted')

    # Check that we still have 4 - 16 players accepted
    if accepted_participants.count() != 4 and accepted_participants.count() != 8:
        return render(request, 'user/play.html', playContext(request, 'Wrong amount of participants', None))

    # Delete Pending, Active and Accepted GameInstances
    for participant in accepted_participants:
        user = participant.user
        all_games = GameInstance.objects.filter(Q(p1=user) | Q(p2=user))
        if all_games.first() is not None:
            all_non_finished_games = all_games.exclude(status='Finished')
            if all_non_finished_games.first() is not None:
                all_non_finished_games.delete()

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

    for p in participants:
        app.consumers.chat_system_message(p.user, "Tournament is starting!")

    return render(request, 'user/play.html', playContext(request, None, 'Tournament started!'))


def tournament_buttons(request):
    try:
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
        return render(request, 'user/play.html', playContext(request, 'error in tournament_buttons()???', None))
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def tournament_forms(request):
    try:
        formname = request.POST.get('formname')
        if formname == 'startTournamentForm':
            return start_tournament(request)
        elif formname == 'tournamentInviteForm':
            return tournament_invite(request)
        elif formname == 'tournamentJoinForm':
            return tournament_join(request)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)
