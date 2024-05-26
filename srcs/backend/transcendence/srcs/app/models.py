from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
import logging


logger = logging.getLogger(__name__)

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
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

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length = 50, unique=True)
    first_name = models.CharField(max_length = 50, null=True)
    last_name = models.CharField(max_length = 50, null=True)
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
    tournament_match = models.BooleanField(default=False)
 
    def __str__(self):
        return f'(Game type: {self.game}, instance: {self.id}, p1: {self.p1.username}, p2: {self.p2.username}, status: {self.status})'


class PongGameInstance(GameInstance):
    longest_rally_hits = models.IntegerField(default=0)
    p1_score = models.IntegerField(default=0)
    p2_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f'({self.game} instance:  p1: {self.p1.username}, p2: {self.p2.username}, status: {self.status})'


class ColorGameInstance(GameInstance):
    turns_to_win = models.IntegerField(default=0)
    
    def __str__(self):
        return f'({self.game} instance:  p1: {self.p1.username}, p2: {self.p2.username}, status: {self.status})'


class Match(models.Model):
    TBD = 'TBD' # We don't know the players yet
    SCHEDULED = 'Scheduled' # We know the players
    ACTIVE = 'Active' # The game is currently being played
    FINISHED = 'Finished' # This match has been finished
    STATUS_CHOICES = [
        (TBD, 'TBD'),
        (SCHEDULED, 'Scheduled'),
        (ACTIVE, 'Active'),
        (FINISHED, 'Finished'),
    ]
    game_instance = models.ForeignKey("GameInstance", on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=SCHEDULED)
    level = models.PositiveIntegerField(default=1)

    def is_last_of_level(self):
        unfinished_matches = self.tournament.match_set.filter(level=self.level).exclude(status='Finished').count()
        return unfinished_matches == 1


class Participant(models.Model):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    READY = 'Ready'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (READY, 'Ready'),
    ]
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)
    alias = models.CharField(max_length=50, default="alias")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        unique_together = ('user', 'tournament')


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
    participants = models.ManyToManyField("CustomUser", through=Participant, related_name="participants")
    matches = models.ManyToManyField("GameInstance", through=Match, related_name="matches")
    
    def get_highest_level(self):
        highest_level = self.match_set.aggregate(max_level=models.Max('level'))['max_level']
        return highest_level if highest_level is not None else 0
