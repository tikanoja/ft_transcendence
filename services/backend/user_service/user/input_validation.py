from .models import CustomUser
import re
from .forms import RegistrationForm

def check_username_availability(username: str):
	exists = CustomUser.objects.filter(username=username)
	if exists:
		raise ValueError("Username is not available")
"""
Password policy
min length: 8
Characters: one of each upercase, lowecase, digit, special 

"""
def check_password_strength(password: str, confirm_password: str):
	if not password == confirm_password:
		raise ValueError("passwords don't match")
	if len(password) < 8:
		raise ValueError("password is too short")
	cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
	special_pattern = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
	match_one = cap_num_pattern.search(password)
	match_two = special_pattern.search(password)
	if not bool(match_one):
		raise ValueError("Password must contain at least one uppercase, one lowercase, and one digit character")
	if not bool(match_two):
		raise ValueError("Password must contain at least one special character")

def check_email(email: str):
	# if email != "":
	exists = CustomUser.objects.filter(email=email)
	if exists:
		raise ValueError("Email is registered with another account")

def validate_registration_input(input):

	form = RegistrationForm(input)
	if not form.is_valid():
		raise ValueError("form incorrectly filled")
	
	password = ""
	confirm_password = ""

	for key, value in input.items():
		if key == "username":
			check_username_availability(value)
		elif key == "email":
			check_email(value)
		elif key == "password":
			password = value
		elif key == "confirm_password":
			confirm_password = value
	check_password_strength(password, confirm_password)


if __name__ == "__main__":
	# attach debuger
	input = {}
	validate_registration_input(input)

