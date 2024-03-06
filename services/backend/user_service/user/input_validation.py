from .models import CustomUser
import re

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
	elif len(password) < 8:
		raise ValueError("password is too short")
	cap_num_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)')
	special_pattern = re.compile('[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]')
	match_one = cap_num_pattern.search(password)
	match_two = special_pattern.search(password)
	if not bool(match_one):
		raise ValueError("Password must contain at least one uppercase, one lowercase, and one digit character")
	if not bool(match_two):
		raise ValueError("Password must contain at least one special character")

def validate_email(email: str):
	# should we actually see if its a real email?
	pass


def screen_input(input: str):
	# check for dangerous inputs
	# not empty,  not sketchy
	# this is done by Django so maybe not needed for now leave empty
	return True


def validate_registration_input(input) -> bool:
	if not input.is_valid():
		raise ValueError("form incorrectly filled")
	password = ""
	confirm_password = ""

	for key, value in input:
		screen_res = screen_input(value)
		if not screen_res:
			return False
		if key is "username":
			check_username_availability(value)
		elif key is "email":
			validate_email(input)
		elif key is "password":
			password = value
		elif key is "confirm_password":
			confirm_password = value
	check_password_strength(password, confirm_password)
	return True


if __name__ == "__main__":
	# attach debuger
	input = {}
	validate_registration_input(input)