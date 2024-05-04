from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
import logging
from django.db import transaction
logger = logging.getLogger(__name__)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields): #add the params needed
        if not username:
            raise ValueError('The username field must be set.')
        if not email:
            raise ValueError('The email field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update_user(self, username, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError('User does not exist')

        if "first_name" in kwargs and "last_name" in kwargs:
            user.first_name = kwargs["first_name"]
            user.last_name = kwargs["last_name"]
        if "email" in kwargs:
            email = self.normalize_email(kwargs["email"])
            user.email = email
        if "password" in kwargs:
            user.set_password(kwargs["password"])
        user.save()

# Create your models here.
class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length = 254, unique=True)
    first_name = models.CharField(max_length = 254, null=True)
    last_name = models.CharField(max_length = 254, null=True)
    email = models.EmailField(max_length = 320, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    blocked_users = models.ManyToManyField('self', related_name='blocked_by', symmetrical=False, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.png')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class Friendship(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    from_user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friend_request_from')
    to_user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friend_request_to')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)


class GameInstance(models.Model):
    PENDING = 'Pending'
    ACTIVE = 'Active'
    ACCEPTED = 'Accepted'
    ERROR = 'Error'
    FINISHED = 'Finished'
    SURRENDER = 'Surrender'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (ACCEPTED, 'Accepted'),
        (ERROR, 'Error'),
        (FINISHED, 'Finished'),
        (SURRENDER, 'Surrender')
    ]

    PONG = 'Pong'
    COLOR = 'Color'
    GAME_CHOICES = [
        (PONG, 'Pong'),
        (COLOR, 'Color'),
    ]

    p1 = models.ForeignKey("CustomUser", related_name="player_one", on_delete=models.SET_NULL, null=True)
    p2 = models.ForeignKey("CustomUser", related_name="player_two", on_delete=models.SET_NULL, null=True)
    p1auth = models.BooleanField(default=False)
    p2auth = models.BooleanField(default=False)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default=PENDING)
    game = models.CharField(max_length=5, choices=GAME_CHOICES, default=PONG)
    winner = models.ForeignKey("CustomUser", related_name="winner", on_delete=models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 

class PongGameInstance(GameInstance):
    longest_rally_time = models.IntegerField(default=0)
    longest_rally_hits = models.IntegerField(default=0)
    total_game_time = models.DurationField()
    p1_hits = models.IntegerField(default=0)
    p2_hits = models.IntegerField(default=0)
    p1_misses = models.IntegerField(default=0)
    p2_misses = models.IntegerField(default=0)
    p1_score = models.IntegerField(default=0)
    p2_score = models.IntegerField(default=0)
    

class ColorGameInstance(GameInstance):
    turns = models.IntegerField(default=0)
    p1_biggest_takeover = models.IntegerField(default=0)
    p2_biggest_takeover = models.IntegerField(default=0)
    

class Match(models.Model):
    # associated tournament
    # player1
    # player2
    pass


class Participant(models.Model):
    # user
    # alias
    pass


class Tournament(models.Model):
    PONG = 'Pong'
    COLOR = 'Color'
    GAME_CHOICES = [
        (PONG, 'Pong'),
        (COLOR, 'Color'),
    ]
    PENDING = 'Pending'
    ACTIVE = 'Active'
    ERROR = 'Error'
    FINISHED = 'Finished'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (ERROR, 'Error'),
        (FINISHED, 'Finished'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    game = models.CharField(max_length=5, choices=GAME_CHOICES, default=PONG)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    creator = models.ForeignKey("CustomUser", related_name="creator", on_delete=models.SET_NULL, null=True)


    # status
    # participants
    # results
    # game instances
    pass


# user profile model
#  language -> maybe add to CustomUser model?
#  picture
#  custom setting for paddle?


# stats model -  individual game stats that linked to the user
#  define what about a game to save
#  expect game service to send game info to us

