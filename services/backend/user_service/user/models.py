from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length = 254, unique=True)
	firstname = models.CharField(max_length = 254)
	lastname = models.CharField(max_length = 254)
	email = models.EmailField(max_length = 254, blank=True, null=True)
	password = models.CharField(max_length = 254)
