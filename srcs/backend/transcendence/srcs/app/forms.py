from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Enter given name'}), max_length=256, required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Enter family name'}), max_length=256, required=True)
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Enter email'}), max_length=320, required=False)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False

        username_exists = CustomUser.objects.filter(username=self.cleaned_data["username"])
        if username_exists:
            raise ValidationError("Username is not available")
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError("passwords don't match")
        del self.cleaned_data['confirm_password']
        if	len(self.cleaned_data['password']) < 8:
            raise ValidationError("password is too short. Must be at least 8 characters")
        cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
        special_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
        match_one = cap_num_pattern.search(self.cleaned_data['password'])
        match_two = special_pattern.search(self.cleaned_data['password'])
        if not bool(match_one):
            raise ValidationError("Password must contain at least one uppercase, one lowercase, and one digit character")
        if not bool(match_two):
            raise ValidationError("Password must contain at least one special character")
        email_exists = CustomUser.objects.filter(email=self.cleaned_data["email"])
        if email_exists:
            raise ValidationError("Email is registered with another account")
        
        return True
        

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class DeleteAccountForm(forms.Form):
    # username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def is_valid(self):
        valid = super().is_valid()
        
        if not valid:
            return False
        elif self.cleaned_data["password"] != self.cleaned_data["confirm_password"]:
            raise ValidationError("Passwords do not match. Please enter your password twice to confirm your account deletion")
        else:
            del self.cleaned_data['confirm_password']
            return True


class UpdatePasswordForm(forms.Form):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    
    def is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False

        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError("passwords don't match")
        del self.cleaned_data['confirm_password']
        if	len(self.cleaned_data['password']) < 8:
            raise ValidationError("password is too short. Must be at least 8 characters")
        cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
        special_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
        match_one = cap_num_pattern.search(self.cleaned_data['password'])
        match_two = special_pattern.search(self.cleaned_data['password'])
        if not bool(match_one):
            raise ValidationError("Password must contain at least one uppercase, one lowercase, and one digit character")
        if not bool(match_two):
            raise ValidationError("Password must contain at least one special character")
        return True
    
class UpdateEmailForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Enter email'}), max_length=320, required=False)

    def	is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False
        email_exists = CustomUser.objects.filter(email=self.cleaned_data["email"])
        if email_exists:
            raise ValidationError("Email is registered with another account")
        return True


class AddFriendForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)

    def is_valid(self):
        valid = super().is_valid()
        
        if not valid:
            return False

        username = self.cleaned_data.get('username')

        if not username or username.isspace():
            raise ValidationError("Empty username")
        
        if not CustomUser.objects.filter(username=self.cleaned_data["username"]).exists():
            raise ValidationError("No such user")
    
        return True


class UpdateNameForm(forms.Form):
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Enter given name'}), max_length=256, required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Enter family name'}), max_length=256, required=True)


class GameRequestForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)
    GAME_TYPE_CHOICES = [
        ('pong', 'Pong'),
        ('color', 'Color'),
    ]
    game_type = forms.ChoiceField(choices=GAME_TYPE_CHOICES, label='Game Type')

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        username = self.cleaned_data.get('username')
        if not username or username.isspace():
            raise ValidationError("Empty username")
        if not CustomUser.objects.filter(username=self.cleaned_data["username"]).exists():
            raise ValidationError("No such user")
        return True 