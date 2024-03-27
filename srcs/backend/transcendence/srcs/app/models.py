from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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

# Create your models here.
class CustomUser(AbstractBaseUser):
	username = models.CharField(max_length = 254, unique=True)
	first_name = models.CharField(max_length = 254, null=True)
	last_name = models.CharField(max_length = 254, null=True)
	email = models.EmailField(max_length = 320, blank=True, null=True)

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()


# user profile model
#  language -> maybe add to CustomUser model?
#  picture
#  custom setting for paddle?


# stats model -  individual game stats that linked to the user
#  define what about a game to save
#  expect game service to send game info to us 
"""
profile/submit_game

request for specific username
{
	GameInstance {
		date: ofGame,
		game: whichGame,
		player1: {
			username: username,
			result: win/loss
			hitRate: percent
		},
		player2: {
			username: username,
			result: win/loss
			hitRate: percent
		}
	},
	GameInstance ...
}
"""