from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.functions import Now
from django.core.exceptions import ValidationError

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
		user = CustomUser.objects.filter(username=username)
		if not user:
			raise ValidationError('user does not exist')
		else:
			user = user[0]
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

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

class Friendship(models.Model):
	PENDING = 'P'
	ACCEPTED = 'A'
	REJECTED = 'R'
	STATUS_CHOICES = [
		(PENDING, 'Pending'),
		(ACCEPTED, 'Accepted'),
		(REJECTED, 'Rejected'),
	]
	from_user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friend_request_from')
	to_user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='friend_request_to')
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)

"""
GameInstance {
		date: ofGame,
		game: pong,
		longest_rally_time: seconds,
		longest_rally_hits: int,
		total_game_time: seconds,
		player1: {
			username: username,
			hits: int,
			misses: int,
			score: int
		},
		player2: {
			username: username,
			hits: int,
			misses: int,
			score: int
		}
	}
"""

class GameInstance(models.Model):
	date = models.DateField(default=Now())
	game = models.CharField(max_length=50)
	longest_rally_time = models.IntegerField(default=0)
	longest_rally_hits = models.IntegerField(default=0)
	total_game_time = models.DurationField()
	p1_user = models.ForeignKey("CustomUser", related_name="player_one", on_delete=models.SET_NULL, null=True)
	p2_user = models.ForeignKey("CustomUser", related_name="player_two", on_delete=models.SET_NULL, null=True)
	p1_hits = models.IntegerField(default=0)
	p2_hits = models.IntegerField(default=0)
	p1_misses = models.IntegerField(default=0)
	p2_misses = models.IntegerField(default=0)
	p1_score = models.IntegerField(default=0)
	p2_score = models.IntegerField(default=0)

	# def __str__(self):


# user profile model
#  language -> maybe add to CustomUser model?
#  picture
#  custom setting for paddle?


# stats model -  individual game stats that linked to the user
#  define what about a game to save
#  expect game service to send game info to us 

