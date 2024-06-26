from django import forms
from .models import CustomUser, GameInstance
from django.core.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username', "class": "form-control"}), max_length=50, required=True)
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Enter given name', "class": "form-control"}), max_length=50, required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Enter family name', "class": "form-control"}), max_length=50, required=True)
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Enter email', "class": "form-control"}), max_length=320, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', "class": "form-control"}), max_length=64, required=True)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', "class": "form-control"}), max_length=64, required=True)

    def is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False

        username = self.cleaned_data["username"]
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        email = self.cleaned_data["email"]

        if not username or username.isspace():
            raise forms.ValidationError("Empty username")
        username_pattern = re.compile(r'^[a-zA-Z0-9]+$')
        username_match = username_pattern.search(self.data['username'])
        if not bool(username_match):
            raise ValidationError("Username may only contain letters and digits")
        username_exists = CustomUser.objects.filter(username=username)
        if username_exists:
            raise ValidationError("Username is not available")

        if password != self.cleaned_data['confirm_password']:
            raise ValidationError("passwords don't match")
        del self.cleaned_data['confirm_password']
        if	len(password) < 8:
            raise ValidationError("password is too short. Must be at least 8 characters")
        cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
        special_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
        match_one = cap_num_pattern.search(password)
        match_two = special_pattern.search(password)
        if not bool(match_one):
            raise ValidationError("Password must contain at least one uppercase, one lowercase, and one digit character")
        if not bool(match_two):
            raise ValidationError("Password must contain at least one special character")

        email_exists = CustomUser.objects.filter(email=email)
        if email_exists:
            raise ValidationError("Email is registered with another account")
        
        return True
        

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username', "class": "form-control"}), max_length=50, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', "class": "form-control"}), max_length=64, required=True)


class PlayerAuthForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Enter password'}), max_length=64, required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in kwargs:
            self.fields['username'] = forms.CharField(widget=forms.HiddenInput(), initial=kwargs['username'])
        if 'game_id' in kwargs:
            self.fields['game_id'] = forms.IntegerField(widget=forms.HiddenInput(), initial=kwargs['game_id'])

class DeleteAccountForm(forms.Form):
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Enter password'}), max_length=64, required=True)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm password'}), max_length=64, required=True)

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
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Enter new password'}), max_length=64, required=True)
    new_confirm_password = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm new password'}), max_length=64, required=True)
    
    def is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False

        if self.cleaned_data['new_password'] != self.cleaned_data['new_confirm_password']:
            raise ValidationError("passwords don't match")
        del self.cleaned_data['new_confirm_password']
        if	len(self.cleaned_data['new_password']) < 8:
            raise ValidationError("Password is too short. Must be at least 8 characters")
        cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
        special_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
        match_one = cap_num_pattern.search(self.cleaned_data['new_password'])
        match_two = special_pattern.search(self.cleaned_data['new_password'])
        if not bool(match_one):
            raise ValidationError("Password must contain at least one uppercase, one lowercase, and one digit character")
        if not bool(match_two):
            raise ValidationError("Password must contain at least one special character")
        return True
    
class UpdateEmailForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Enter email', 'class': 'form-control'}), max_length=320, required=True)

    def	is_valid(self):
        valid = super().is_valid()

        if not valid:
            return False
        email_exists = CustomUser.objects.filter(email=self.cleaned_data["email"])
        if email_exists:
            raise ValidationError("Email is registered with another account")
        return True


class AddFriendForm(forms.Form):
    username = forms.CharField(label='Username to friend or block', widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'class':'form-control'}), max_length=50, required=True)

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
    first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Enter given name', 'class': 'form-control'}), max_length=50, required=True)
    last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Enter family name', 'class': 'form-control'}), max_length=50, required=True)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["profile_picture"]


class GameRequestForm(forms.Form):
    GAME_TYPE_CHOICES = [
        (GameInstance.PONG, 'Pong'),
        (GameInstance.COLOR, 'ColorWar'),
    ]
    
    game_type = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), choices=GAME_TYPE_CHOICES, label='Choose Game Type:')
    username = forms.CharField(label='Enter username', widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-control'}), max_length=50, required=True)

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


class LocalGameForm(forms.Form):
    GAME_TYPE_CHOICES = [
        (GameInstance.PONG, 'Pong'),
        (GameInstance.COLOR, 'ColorWar'),
    ]
    game_type = forms.ChoiceField(choices=GAME_TYPE_CHOICES, label='Game Type')
    username = forms.CharField(label='P2 Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=50, required=True)
    password = forms.CharField(label='P2 Password', widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}), max_length=64, required=True) #max_length=50
    
    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not username or username.isspace():
            raise forms.ValidationError("Empty username")
        if not password or password.isspace():
            raise forms.ValidationError("Empty password")
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError("No such user")
        if not user.check_password(password):
            raise forms.ValidationError("Incorrect password")
        return True

class StartTournamentForm(forms.Form):
    GAME_TYPE_CHOICES = [
        (GameInstance.PONG, 'Pong'),
        (GameInstance.COLOR, 'ColorWar'),
    ]
    game_type = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), choices=GAME_TYPE_CHOICES, label='Choose Game Type:')
    alias = forms.CharField(label='Enter alias', widget=forms.TextInput(attrs={'placeholder': 'Enter alias', 'class': 'form-control'}), max_length=50, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'formname' in kwargs:
            self.fields['formname'] = forms.CharField(widget=forms.HiddenInput(), initial=kwargs['formname'])


class TournamentInviteForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-control'}), max_length=50, required=True)

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'formname' in kwargs:
            self.fields['formname'] = forms.CharField(widget=forms.HiddenInput(), initial=kwargs['formname'])

class TournamentJoinForm(forms.Form):
    alias = forms.CharField(label='Alias', widget=forms.TextInput(attrs={'placeholder': 'Enter alias', 'class': 'form-control'}), max_length=50, required=True)
