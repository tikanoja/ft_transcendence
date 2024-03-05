from django import forms

class RegistrationForm(forms.Form):
	username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}), max_length=256, required=True)
	first_name = forms.CharField(label='First Name', widget=forms.TextInput(attrs={'placeholder': 'Enter given name'}), max_length=256, required=True)
	last_name = forms.CharField(label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Enter family name'}), max_length=256, required=True)
	email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Enter email'}), max_length=320, required=False)
	password = forms.CharField(label="Password", widget=forms.PasswordInput)
	confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
