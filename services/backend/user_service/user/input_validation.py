
def check_username_availability(username: str):
	# query db to see if name is taken
	pass

"""
Password policy
min length:

"""
def check_password_strength(password: str):
	# create three tiers and enforce a policy
	pass


def validate_email(email: str):
	# should we actually see if its a real email?
	pass


def screen_input(input: str):
	# check for dangerous inputs
	# not empty,  not sketchy
	pass


def validate_registration_input(input) -> bool:
	# call all validation funcs
	for key, value in input:
		screen_res = screen_input(value)
		if not screen_res:
			# make a reason for the fail visible in the result
			return False
		if key is "username":
			check_username_availability(value)
		elif key is "email":
			validate_email(input)
		elif key is "password":
			check_password_strength(value)
	return True


if __name__ == "__main__":
	# attach debuger
	input = {}
	validate_registration_input(input)