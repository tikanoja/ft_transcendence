import sys

def prGreen(input): print("\033[92m{}\033[00m" .format(input))
def prRed(input): print("\033[91m{}\033[00m" .format(input))


prGreen("""██████╗  ██████╗ ███╗   ██╗ ██████╗ 
██╔══██╗██╔═══██╗████╗  ██║██╔════╝ 
██████╔╝██║   ██║██╔██╗ ██║██║  ███╗
██╔═══╝ ██║   ██║██║╚██╗██║██║   ██║
██║     ╚██████╔╝██║ ╚████║╚██████╔╝
╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝    
                                    """)

def interactive_cli():
	print("entering interactive mode: instructions would go here ie which game game settings etc")
	print("1: get number of games in progress")
	print("2: get scores of games in progress")
	print("3: access user dashboard")
	user_input = input("basic command input: ")
	if user_input == '3':
		print("""
		Username:
		win percentage:
		loss percentage:
		last game against:""")
	print("attempt to run command")


def main():

	print("command entered was: ",  sys.argv)
	
	if len(sys.argv) == 1:
			prRed("This will one day hold the help menu")
	elif len(sys.argv) == 2 and sys.argv[1] == "-I":
		interactive_cli()
	else:
		print("attempt to run command")


if __name__ == "__main__":
	main()