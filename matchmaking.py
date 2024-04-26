import random
import string

class colors:
    HEADER = '\033[96m'
    OKGREEN = '\033[92m'
    OKPINK = '\033[95m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text, color):
    print(color + text + colors.ENDC)

class Competitor:
    def __init__(self):
        self.username = None
        self.knocked_out = False
        self.games_played = 0
        self.win_percent = 0
        self.ranking = 0

class Match:
    def __init__(self):
        self.player_1 = None
        self.player_2 = None
        self.status = None
        self.winner = None

def generate_username():
    animal = ['Tiger','Eagle', 'Dolphin', 'Elephant', 'Lion', 'Octopus', 'Giraffe', 'Penguin', 'Koala', 'Cheetah']
    adjectives = ['Majestic', 'Agile', 'Graceful', 'Fierce', 'Wise', 'Playful', 'Elegant', 'Swift', 'Loyal', 'Curious']

    username = adjectives[random.randint(0,9)] + "_" + animal[random.randint(0,9)] 
    return username

def print_competitor(comp):
    print(colors.OKPINK + "UserName:   " + str(comp.username)  + colors.ENDC)
    print(colors.OKPINK + "games_played:   "  + str(comp.games_played) + colors.ENDC)
    print(colors.OKPINK + "win_percent:   "  + str(comp.win_percent) + colors.ENDC)
    print(colors.OKPINK + "ranking:   "  + str(comp.ranking) + colors.ENDC)
    print(colors.OKPINK + "knocked_out:   " + str(comp.knocked_out)  + colors.ENDC)

def random_gen_competitors():
    # Generate competitors (dummy data for starting)
    competitors = []
    for i in range(1, 7):
        comp = Competitor()
        comp.games_played = random.randint(1,200)
        comp.win_percent = random.randint(0,100)
        comp.ranking = i
        comp.username = generate_username()
        competitors.append(comp)
    return competitors

def sort_initial_ranking(competitors):
    if len(competitors) < 2:
        return competitors

    low, same, high, ranking = [], [], [], []

    pivot = competitors[random.randint(0, len(competitors) - 1)].games_played

    for item in competitors:
        if not item.knocked_out:
            if item.games_played < pivot:
                low.append(item)
            elif item.games_played == pivot:
                same.append(item)
            elif item.games_played > pivot:
                high.append(item)
    ranking = sort_initial_ranking(high) + same + sort_initial_ranking(low)
    for i, competitor in enumerate(ranking, 1):
        competitor.ranking = i
    return ranking

def create_matches(competitors):
    matches = []
    i = len(competitors)
    if i % 2 == 0:  # Even number of players
        while i > 0:
            match = Match()
            match.player_1 = competitors[i - 1]
            match.player_2 = competitors[i - 2]
            matches.append(match)
            i -= 2
    else:
        highest_ranked = max(competitors, key=lambda x: x.ranking)
        for competitor in competitors:
            if competitor != highest_ranked:
                match = Match()
                match.player_1 = highest_ranked
                match.player_2 = competitor
                matches.append(match)
        i -= 1
    return matches

def print_competitor_array(competitors):
    for i, competitor in enumerate(competitors):
        print(f"Competitor {i+1}:")
        print_competitor(competitor)
        print()

def print_matches(matches):
    for i, match in enumerate(matches):
        print_color(colors.OKGREEN, f"match {i+1}:")
        print(match.player_1.username)
        print(match.player_2.username)
        if match.winner != None:
            print("Winner: " + match.winner.username)
        print()

def set_games_to_in_progress(matches):
    print_color(colors.OKGREEN, "setting matches it in_progress")
    for match in matches:
        match.status = "in_progress"
        print()

def set_losers_game_over(matches):
    print_color(colors.OKGREEN, "setting matches it in_progress")
    for match in matches:
        match.status = "done"
        match.winner = match.player_1
        match.player_2.knocked_out = True
        match.player_2.ranking = 0


if __name__ == "__main__":
    #TODO: needs to get the users information and load it into the classes and then as it is in progress update the pairing
    
    #TODO: get competitors from API    
    competitors = random_gen_competitors()
    ranking = sort_initial_ranking(competitors)
    print_competitor_array(ranking)
    print("-----------after----------")
    matches = create_matches(ranking)
    # print_matches(matches)

    #TODO: send matches and wait for responses on wins and losses
    set_games_to_in_progress(matches)
    #TODO: wait for all the games to be done.

    set_losers_game_over(matches)
    print_matches(matches)

    ranking = sort_initial_ranking(ranking)
    # print_competitor_array(ranking)
    print_competitor_array(competitors)
