from django.utils import timezone
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.db.models import Q
from app.models import CustomUser, GameInstance, Friendship
from app.forms import AddFriendForm
from django.http import JsonResponse
import json
import logging


logger = logging.getLogger(__name__)


def friendsContext(username, error, success):
    form = AddFriendForm()
    title = "Manage friends"
    current_user = CustomUser.objects.filter(username=username).first()
    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))

    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)
    blocked_users = current_user.blocked_users.all()

    for friendship in friendships:
        other_user = friendship.from_user if friendship.from_user != current_user else friendship.to_user
        if other_user.is_online and timezone.now() - other_user.last_seen > timezone.timedelta(minutes=42):
            other_user.is_online = False
            other_user.save()

    if not error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users}
    elif error and not success:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users, 'error': error}
    else:
        context = {'current_user': current_user, 'form': form, 'title': title, 'in_invites': in_invites, 'out_invites': out_invites, 'friendships': friendships, 'blocked_users': blocked_users, 'success': success}
    return context


def friendsGET(request):
    return render(request, 'user/profile_partials/friends.html', friendsContext(request.user.username, None, None))	


def friendResponse(request, data):
    from_username = data.get('from_user')
    from_user = CustomUser.objects.filter(username=from_username).first()
    if not from_user:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Could not find the friend candidate", None), "self_profile": True})    
    action = data.get('action')

    if action == 'unblock':
        request.user.blocked_users.remove(from_user)
        request.user.save()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Unblocked " + from_user.username), "self_profile": True})

    friendship = Friendship.objects.filter(Q(to_user=request.user, from_user=from_user) | Q(to_user=from_user, from_user=request.user)).first()
    if not friendship:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Could not find the friendship", None), "self_profile": True})    

    if action == 'accept':
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Congratulations, you made a new friend!"), "self_profile": True})
    elif action == 'reject':
        friendship.delete()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friendship REJECTED!"), "self_profile": True})
    elif action == 'delete':
        friendship.delete()
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friendship DELETED!"), "self_profile": True})


def friendsPOST(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        if data.get('request_type') == 'friendResponse':
            return friendResponse(request, data)
        else:
            return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, ve, "Unknown content type"), "self_profile": True})

    sent_form = AddFriendForm(request.POST)
    try:
        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")
    except ValidationError as ve:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, ve, None), "self_profile": True})
    friend_username = sent_form.cleaned_data['username']
    current_user = request.user
    friend_user = CustomUser.objects.filter(username=friend_username).first()
    if friend_user in current_user.blocked_users.all() or current_user in friend_user.blocked_users.all():
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You cannot add or request friendship with a blocked user", None), "self_profile": True})

    # check if they are trying to add themselves
    if request.user.username == friend_username:
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "Please do not add yourself", None), "self_profile": True})

    # all friendships where current_user is: no matter the status
    all_friendships = Friendship.objects.filter(Q(from_user=current_user) | Q(to_user=current_user))
    # all accepted friendships where current_user is
    friendships = all_friendships.filter(status=Friendship.ACCEPTED)
    # pending friend requests coming for current_user
    in_invites = all_friendships.filter(to_user=current_user, status=Friendship.PENDING)
    # the request current_user has sent out to other users
    out_invites = all_friendships.filter(from_user=current_user, status=Friendship.PENDING)

    # check if they are already friends
    if friendships.filter(Q(from_user=friend_user) | Q(to_user=friend_user)):
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You are already friends", None), "self_profile": True})

    # check if friend_user matches an incoming invite, and if yes, update the status of that Friendship to ACCEPTED
    incoming_invite = in_invites.filter(from_user=friend_user)
    if incoming_invite.exists():
        incoming_invite.update(status=Friendship.ACCEPTED)
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Congratulations, you made a new friend!"), "self_profile": True})

    # check if they have already sent a request to the user in question
    if out_invites.filter(to_user=friend_user):
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, "You have already sent a request to this user", None), "self_profile": True})

    # add to friends
    new_friendship = Friendship(from_user=current_user, to_user=friend_user, status=Friendship.PENDING)
    new_friendship.save()

    return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Friend request sent"), "self_profile": True})


def block_user(request):
    try:
        sent_form = AddFriendForm(request.POST)

        if not sent_form.is_valid():
            raise ValidationError("Form filled incorrectly")

        blocked_username = sent_form.cleaned_data['username']
        blocked_user = CustomUser.objects.get(username=blocked_username)

        as_user_block_user(request.user, blocked_user)
    except ValidationError as e:
        error_message = e.message if hasattr(e, "message") else str(e)
        return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, error_message, None), "self_profile": True})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'user/profile_partials/friends.html', {"friends": friendsContext(request.user.username, None, "Blocked " + blocked_username + "!"), "self_profile": True})


def as_user_block_user(user: CustomUser, blocked: CustomUser):
    if user.username == blocked.username:
        raise ValidationError("Please do not block yourself")

    if blocked in user.blocked_users.all():
        raise ValidationError("You have already blocked " + blocked.username)

    # Delete possible friendship between them
    friendships_to_delete = Friendship.objects.filter(Q(from_user=user, to_user=blocked) | Q(from_user=blocked, to_user=user))
    friendships_to_delete.delete()

    # Delete pending game invites
    game_instances_to_delete = GameInstance.objects.filter(Q(p1=user, p2=blocked) | Q(p2=blocked, p1=user), status='Pending')
    game_instances_to_delete.delete()

    # Add to blocked
    user.blocked_users.add(blocked)
    user.save()
