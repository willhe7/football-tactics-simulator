import random
import time
import os
import sys
import json
import math

if getattr(sys, 'frozen', False):
    # Running in a bundled .exe
    base_path = sys._MEIPASS
else:
    # Running normally from source
    base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)
# Ensures JSON files are read/written from the script's own folder

role_options = {
    "GK": ["Goalkeeper (Defend)"],
    "LB": ["Fullback (Defend)", "Fullback (Support)", "Fullback (Attack)",
           "Inverted Wingback (Defend)", "Inverted Wingback (Support)", "Inverted Wingback (Attack)"],
    "RB": ["Fullback (Defend)", "Fullback (Support)", "Fullback (Attack)",
           "Inverted Wingback (Defend)", "Inverted Wingback (Support)", "Inverted Wingback (Attack)"],
    "CB": ["Centreback (Defend)", "Centreback (Stopper)", "Centreback (Cover)",
           "Ball Playing Defender (Defend)", "Ball Playing Defender (Stopper)", "Ball Playing Defender (Cover)", "Libero (Support)", "Libero (Attack)"],
    "LW": ["Winger (Support)", "Winger (Attack)", "Inside Forward (Support)", "Inside Forward (Attack)",
           "Wide Target Forward (Support)", "Wide Target Forward (Attack)", "Wide Playmaker (Support)", "Wide Playmaker (Attack)"],
    "RW": ["Winger (Support)", "Winger (Attack)", "Inside Forward (Support)", "Inside Forward (Attack)",
           "Wide Target Forward (Support)", "Wide Target Forward (Attack)", "Wide Playmaker (Support)", "Wide Playmaker (Attack)"],
    "CM": ["Central Midfielder (Defend)", "Central Midfielder (Support)", "Central Midfielder (Attack)",
           "Box to Box Midfielder (Support)", "Ball Winning Midfielder (Defend)", "Ball Winning Midfielder (Support)", "Playmaker (Support)"],
    "ST": ["Advanced Forward (Attack)", "Poacher (Attack)", "Target Forward (Support)", "Target Forward (Attack)",
           "False Nine (Support)", "Complete Forward (Support)", "Complete Forward (Attack)"],
}

def clear():
    # Wipes the page
    os.system("cls" if os.name == "nt" else "clear")

def writeteamdata(newdata, place, edit):
    # Saves a specific key-value pair to a team save file (e.g. 'coins', 'squad', 'team')
    f = open("teamdata" + str(edit) + ".json", "r")
    data = json.load(f)
    f.close()
    data[place] = newdata
    f = open("teamdata" + str(edit) + ".json", "w")
    json.dump(data, f)
    f.close()
    
def readteamdata(place, edit):
    # Reads a specific value from a save file by key (e.g. 'formation', 'gamesremaining')
    f = open("teamdata" + str(edit) + ".json", "r")
    data = json.load(f)
    f.close()
    return data[place]

def invalid(page):
    page()

def invalidpack(coinspacks):
    if coins < coinspacks:
        clear()
        time.sleep(1)
        print("")
        print("ERROR: Not enough coins")
        print("")
        time.sleep(1)
        storepage()
        
def removeopponent(edit):
    filename = f"teamdata{edit}.json"
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
    # Load the team data
    with open(filename, "r") as f:
        data = json.load(f)
    # Remove the opponent key if it exists
    if "opponent" in data:
        del data["opponent"]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    else:
        print(f"No 'opponent' key found in {filename}.")        
    
def formationswitch(newformation):
    # Returns player positions and chemistry links for a given formation
    # Used to display formation layout and possible player links
    player = [{} for _ in range(12)] 
    # Initialise 11 player slots (1-indexed) as empty dictionaries
    playerlink = {}
    # Store which players are connected (linked) for chemistry
    # 4-4-2 formation
    if newformation == "4-4-2":
        position = ["GK", "LB", "CB", "CB", "RB", "LW", "CM", "CM", "RW", "ST", "ST"]
        linkpair = [[1,3], [1,4], [2,3], [2,6], [3,7], [3,4], [4,5], [4,8], [5,9],
                    [6,7], [7,8], [7,10], [8,9], [8,11], [10,11]]
    # 4-3-3 formation
    elif newformation == "4-3-3":
        position = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]
        linkpair = [[1,3], [1,4],[2,3], [2,6], [3,4], [3,6], [3,7], [4 ,5], [4,7], 
                    [4,8], [5,8], [6,7], [6,9], [7,8], [7,10], [8,11], [9,10], [10,11]]

    # 4-5-1 formation
    elif newformation == "4-5-1":
        position = ["GK", "LB", "CB", "CB", "RB", "LW", "CM", "CM", "CM", "RW", "ST"]
        linkpair = [[1,3], [1,4], [2,3], [2,6], [2,7], [3,4], [3,7], [3,8], [4,5],
                    [4,8], [4,9], [5,9], [5,10], [6,7], [7,8], [8,9], [8,11], [9,10]]
    # 4-2-2-2 formation
    elif newformation == "4-2-2-2":
        position = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "CM", "ST", "ST"]
        linkpair = [
            (1, 3), (1, 4),       # GK ↔ back four
            (2, 3), (3, 4), (4, 5),               # across defence
            (3, 6), (4, 7),                       # LCB↔LDM, RCB↔RDM
            (6, 8), (7, 9),                       # LDM↔LAM, RDM↔RAM
            (8, 10), (9, 11),                     # LAM↔LST, RAM↔RST
            (10, 11),                             # between strikers
        ]
    # 5-3-2 formation
    elif newformation == "5-3-2":
        position = ["GK", "LB", "CB", "CB", "CB", "RB", "CM", "CM", "CM", "ST", "ST"]
        linkpair = [[1,3], [1,4], [1,5], [2,3], [3,4], [3,7], [4,5], [4,8], [5,6],
                    [5,9], [7,8], [7,10], [8,9], [8,10], [8,11], [9,11], [10,11]]
    # 5-2-3 formation
    elif newformation == "5-2-3":
        position = ["GK", "LB", "CB", "CB", "CB", "RB", "CM", "CM", "LW", "ST", "RW"]
        linkpair = [[1,3], [1,4], [1,5], [2,3], [3,4], [3,7], [4,5], [4,7], [4,8],
                    [5,6], [5,8], [7,8], [7,9], [7,10], [8,10], [8,11], [9,10], [10,11]]
    # 5-4-1 formation
    elif newformation == "5-4-1":
        position = ["GK", "LB", "CB", "CB", "CB", "RB", "LW", "CM", "CM", "RW", "ST"]
        linkpair = [[1,3], [1,4], [1,5], [2,3], [3,4], [3,7], [3,8], [4,5], [4,8],
                    [4,9], [5,6], [5,9], [5,10], [6,10], [7,8], [8,9], [8,11], [9,10], [9,11]]
    # Assign position name to each player slot
    for i in range(1, 12):
        player[i]["position"] = position[i - 1]
        playerlink[i] = []
    # Define chemistry links between player slots
    for a, b in linkpair:
        playerlink[a].append(b)
        playerlink[b].append(a)
    return player, playerlink

def quicksell(rating):
  rating = int(rating)
  if rating < 50:
    rating = 0
  elif rating <= 54:
    rating2 = rating - 50
    rating = 10 + rating2*5
  elif rating <= 64:
    rating2 = rating - 55
    rating = 10 + rating2*10
  elif rating <= 74:
    rating2 = rating - 65
    rating = 120 + rating2*20
  elif rating <= 82:
    rating2 = rating - 75
    rating = 320 + rating2*150
  elif rating <= 87:
    rating2 = rating - 83
    rating = 1000 + rating2*500
  else:
    rating2 = rating - 88
    rating = 10000 + rating2*5000
  return rating

def quicksellplayer(player):
    clear()
    print("")
    print("QUICKSELL")
    print("")
    print("Are you sure you want to quicksell?")
    print("")
    print("Yes - Y")
    print("No  - N")
    print("")
    quicksellinput = input().lower()
    if quicksellinput == "n":
        return
    elif quicksellinput != "y":
        quicksellplayer(player)
    squad = readteamdata("squad", edit)
    if len(squad) <= 11:
        clear()
        print("")
        print("You must have more than 11 players to quicksell")
        print("")
        time.sleep(2)
    else:
        # If allowed, remove the player and give coins
        squad = [p for p in squad if p["name"] != player["name"]]
        writeteamdata(squad, "squad", edit)
        global coins
        coins += quicksell(player["rating"])
        writeteamdata(str(coins), "coins", edit)
        clear()
        print("")
        print(f"{player['name']} quicksold for {quicksell(player['rating'])} coins")
        print("")
        time.sleep(2)

def teamrating():
    squad = readteamdata("squad", edit)[:11]
    totalrating = sum(p["rating"] for p in squad)
    # Rounds down
    return totalrating // 11 

def teamchemistry(opponent=False):
    if opponent:
        data = readteamdata("opponent", edit)
        squad = data["players"][:11]
    else:
        squad = readteamdata("squad", edit)[:11]
    totalchem = 0
    for player in squad:
        chem, _ = chemistry(player["name"], opponent=opponent)
        if chem is not None:
            totalchem += chem
    return min(100, totalchem)

def chemistry(playername, opponent = False):
    if opponent:
        data = readteamdata("opponent", edit)
        squad = data["players"]
        formation = data["formation"]
        managercountry = data.get("manager country", "")
    else:
        squad = readteamdata("squad", edit)[:11]
        formation = readteamdata("formation", edit)
        managercountry = readteamdata("manager country", edit)
    playerslots, playerlinks = formationswitch(formation)
    def getcategory(pos):
        pos = pos.strip().upper()
        if pos in ["GK"]:
            return "GK"
        elif pos in ["LB", "CB", "RB"]:
            return "DEF"
        elif pos in ["CM"]:
            return "MID"
        elif pos in ["LW", "RW", "ST"]:
            return "ATT"
        else:
            return "OTHER"
    # Find player index (1-based)
    index = None
    for i, p in enumerate(squad):
        if p["name"] == playername:
            index = i + 1
            break
    if index is None:
        return None, None
    player = squad[index - 1]
    expected_pos = playerslots[index]["position"].strip().upper()
    actual_pos = player["position"].strip().upper()
    chemistrylevel = 2
    # --- Position logic ---
    in_position = actual_pos == expected_pos
    if not in_position:
        cat_actual = getcategory(actual_pos)
        cat_expected = getcategory(expected_pos)
        if "GK" in [cat_actual, cat_expected]:
            finalrating = player["rating"] - 40
            player["chemistrylevel"] = 0
            player["finalrating"] = finalrating
            return 0, finalrating
        elif cat_actual == cat_expected:
            chemistrylevel -= 2
        else:
            chemistrylevel -= 5
    # --- Link logic ---
    linked_indexes = playerlinks.get(index, [])
    matched_links = 0
    for link_index in linked_indexes:
        if link_index <= len(squad):
            teammate = squad[link_index - 1]
            if teammate["country"] == player["country"]:
                matched_links += 1
    # Apply custom link bonus
    total_links = len(linked_indexes)
    if total_links == 1:
        chemistrylevel += 8 * matched_links
    elif total_links == 2:
        chemistrylevel += 4 * matched_links
    elif total_links == 3:
        chemistrylevel += 3 * matched_links
    elif total_links > 3:
        chemistrylevel += 3 * matched_links
    # Perfect chemistry override
    if in_position and matched_links == total_links and total_links > 0:
        chemistrylevel = 10
    # Manager country bonus
    if player["country"] == managercountry:
        chemistrylevel += 3
    # Clamp chemistry
    chemistrylevel = min(10, max(0, chemistrylevel))
    # Final rating adjustment
    role = player.get("role", "Goalkeeper (Defend)")
    role_rating = rolerating(player["name"], role)
    if role_rating is None or (role.startswith("Goalkeeper") and role_rating == 0):
        role_rating = player["rating"]
    if chemistrylevel == 0:
        finalrating = role_rating - 5
    elif chemistrylevel == 1:
        finalrating = role_rating - 4
    elif chemistrylevel == 2:
        finalrating = role_rating - 3
    elif chemistrylevel == 3:
        finalrating = role_rating - 2
    elif chemistrylevel == 4:
        finalrating = role_rating - 1
    elif chemistrylevel == 5:
        finalrating = role_rating + 0
    elif chemistrylevel == 6:
        finalrating = role_rating + 1
    elif chemistrylevel == 7:
        finalrating = role_rating + 2
    elif chemistrylevel == 8:
        finalrating = role_rating + 3
    elif chemistrylevel == 9:
        finalrating = role_rating + 4
    elif chemistrylevel == 10:
        finalrating = role_rating + 5
    else:
        finalrating = rolerating
    # Cap at 99
    finalrating = min(finalrating, 99)
    player["chemistrylevel"] = chemistrylevel
    player["finalrating"] = finalrating
    return chemistrylevel, finalrating

def categoryratings(opponent=False, category=None):
    # Read the appropriate team data depending on whether it's the opponent or the user's team
    squad = readteamdata("opponent" if opponent else "squad", edit)
    formation = readteamdata("formation", edit)
    # Get positional slots and links from the chosen formation
    playerslots, _ = formationswitch(formation)
    # Map in-game positions to broader categories: DEF, MID, ATT
    categorymap = {
        "GK": "DEF", "LB": "DEF", "CB": "DEF", "RB": "DEF",
        "CM": "MID",
        "LW": "ATT", "RW": "ATT", "ST": "ATT"
    }

    # Helper to get the general category for a given position
    def getcategory(pos):
        return categorymap.get(pos.strip().upper(), "OTHER")

    # Initialise rating lists for each outfield category
    ratingsbycat = {"DEF": [], "MID": [], "ATT": []}
    # Loop through each of the starting 11 players
    for i, player in enumerate(squad[:11]):
        # Find the assigned position from the formation
        slotpos = playerslots[i + 1]["position"]
        playercat = getcategory(slotpos)
        # If the position maps to one of our tracked categories, compute their final rating
        if playercat in ratingsbycat:
            _, finalrating = chemistry(player["name"], opponent)
            ratingsbycat[playercat].append(finalrating)
    # If a specific category is requested, return its average (rounded down)
    if category:
        category = category.upper()
        if category in ratingsbycat and ratingsbycat[category]:
            return math.floor(sum(ratingsbycat[category]) / len(ratingsbycat[category]))
        else:
            return None
    else:
        # Return a dictionary of all categories with their respective average ratings (rounded down)
        return {
            cat: math.floor(sum(ratings)/len(ratings)) if ratings else None
            for cat, ratings in ratingsbycat.items()
        }

class Player:
    # Defines a player object with name, country, position, rating, and stats
    # Supports display in terminal and conversion to/from dictionary format for saving/loading

    def __init__(self, name, country, position, rating, stats):
        # Initialise a new Player instance with given attributes
        self.name = name
        self.country = country
        self.position = position
        self.rating = rating
        self.stats = stats

    def display(self):
        # Prints the player's full information in a readable format
        print(f"Name: {self.name}")
        print(f"Country: {self.country}")
        print(f"Position: {self.position}")
        print(f"Rating: {self.rating}")
        print("Stats:")
        for stat, value in self.stats.items():
            print(f"  {stat.capitalize()}: {value}")
        print()

    def to_dict(self):
        # Converts the player object into a dictionary (used for saving as JSON)
        return {
            "name": self.name,
            "country": self.country,
            "position": self.position,
            "rating": self.rating,
            "stats": self.stats
        }

    @classmethod
    def from_dict(cls, data):
        # Creates a Player object from a dictionary (used when loading from JSON)
        return cls(
            data["name"],
            data["country"],
            data["position"],
            data["rating"],
            data["stats"]
        )

def playerview(players, title, returncallback, activecountryfilters=None, activepositionfilters=None):
    # Displays players in a page-like list
    # Applies country and position filters if enabled
    if activecountryfilters is None:
        activecountryfilters = set()
    if activepositionfilters is None:
        activepositionfilters = set()
    pagesize = 10
    filtered = []
    # Filter players based on active country/position filters
    for p in players:
        country_ok = not activecountryfilters or p["country"] in activecountryfilters
        position_ok = not activepositionfilters or p["position"] in activepositionfilters
        if country_ok and position_ok:
            filtered.append(p)
    totalpages = (len(filtered) + pagesize - 1) // pagesize
    currentpage = 0
    while True:
        clear()
        print("")
        print(f"{title} - Page {currentpage + 1} of {totalpages}\n")
        print("")
        time.sleep(2)
        if not players:
            print("No players match the selected filters.")
            print("")
            print("Return - R")
            print("")
            playerviewinput = input()
            mysquadpage(returncallback)
        start = currentpage * pagesize
        end = start + pagesize
        for p in filtered[start:end]:
            # Display players on the current page using the Player class
            player = Player.from_dict(p)
            player.display()
            print("")
        if currentpage > 0:
            print("Previous Page      - P")
        if currentpage < totalpages - 1:
            print("Next Page          - N")
        if totalpages != 1:
            print(f"Enter page number (1–{totalpages})")
        print("Apply Filters      - F")
        print("Return             - R")
        print("")
        pageinput = input().lower()
        if pageinput == "p" and currentpage > 0:
            # Move to previous page
            currentpage -= 1
        elif pageinput == "n" and currentpage < totalpages - 1:
            # Move to next page
            currentpage += 1
        elif pageinput.isdigit():
            # Jump to a specific page
            page = int(pageinput)
            if 1 <= page <= totalpages:
                currentpage = page - 1
        elif pageinput == "f":
            # Open filter menu
            playerviewfilters(players, title, returncallback, activecountryfilters, activepositionfilters)
            return
        elif pageinput == "r":
            # Return to previous menu
            returncallback()

def playerviewfilters(players, title, returncallback, countryfilters, positionfilters):
    # Displays filter menu for narrowing players by country or position
    while True:
        clear()
        print("")
        print("FILTER OPTIONS")
        print("")
        print("Filter by Country  - 1")
        print("Filter by Position - 2")
        print("")
        print("Return             - 3")
        print("")
        mysquadpageinput = input().strip()
        if mysquadpageinput == "1":
            # Open country filter toggle menu
            playerviewfiltercountry(players, title, returncallback, countryfilters, positionfilters)
            return
        elif mysquadpageinput == "2":
            # Open position filter toggle menu
            playerviewfilterposition(players, title, returncallback, countryfilters, positionfilters)
            return
        elif mysquadpageinput == "3":
            # Apply current filters and return to player view
            playerview(players, title, returncallback, countryfilters, positionfilters)
            return

def playerviewfiltercountry(players, title, returncallback, countryfilters, positionfilters):
    # Toggle which countries to filter (can apply multiple)
    countries = sorted(set(p["country"] for p in players))
    # Generate a sorted list of all unique countries in the player data
    while True:
        clear()
        print("")
        print("COUNTRY FILTERS (toggle)")
        print("")
        for i, c in enumerate(countries, 1):
            # Show which countries are currently applied as filters
            tag = " (Applied)" if c in countryfilters else ""
            print(f"{c:<12} - {i}{tag}")
        print("")
        print(f"Return       - {len(countries) + 1}")
        print("")
        mysquadpageinput = input().strip()
        if mysquadpageinput.isdigit():
            idx = int(mysquadpageinput)
            if 1 <= idx <= len(countries):
                country = countries[idx - 1]
                # Toggle selected country on or off
                if country in countryfilters:
                    countryfilters.remove(country)
                else:
                    countryfilters.add(country)
            elif idx == len(countries) + 1:
                # Return to the filter menu
                break
    playerviewfilters(players, title, returncallback, countryfilters, positionfilters)

def playerviewfilterposition(players, title, returncallback, countryfilters, positionfilters):
    # Toggle which positions to filter (ordered for usability)
    preferredorder = ["GK", "LB", "CB", "RB", "CM", "LW", "RW", "ST"]
    # Define preferred display order to make filters easier to navigate
    positions = sorted(set(p["position"] for p in players), key=lambda x: preferredorder.index(x) if x in preferredorder else 99)
    # Extract unique positions from all players and sort by the preferred order
    while True:
        clear()
        print("")
        print("POSITION FILTERS (toggle)")
        print("")
        for i, pos in enumerate(positions, 1):
            # Show which positions are currently applied as filters
            tag = " (Applied)" if pos in positionfilters else ""
            print(f"{pos:<6} - {i}{tag}")
        print("")
        print(f"Return - {len(positions) + 1}")
        print("")
        mysquadpageinput = input().strip()
        if mysquadpageinput.isdigit():
            idx = int(mysquadpageinput)
            if 1 <= idx <= len(positions):
                pos = positions[idx - 1]
                # Toggle selected position on or off
                if pos in positionfilters:
                    positionfilters.remove(pos)
                else:
                    positionfilters.add(pos)
            elif idx == len(positions) + 1:
                # Return to filter menu
                break
    playerviewfilters(players, title, returncallback, countryfilters, positionfilters)

def playerviewstore(low, high):
    # View all players in a given rating range for browsing
    clear()
    f = open("ratings.json", "r")
    players = json.load(f)
    f.close()
    # Load all player data from file and filter based on rating range
    filteredplayers = [p for p in players if low <= p["rating"] <= high]
    pagesize = 10
    totalpages = (len(filteredplayers) + pagesize - 1) // pagesize
    currentpage = 0
    # Show page-like player view using the existing playerview function
    while True:
        playerview(filteredplayers, f"{low}–{high} OVR PLAYERS", viewallplayerspage, set(), set())

def viewallplayerspage():
    clear()
    print("")
    print("VIEW ALL PLAYERS")
    print("")
    print("87-94 OVR - 1")
    print("80-86 OVR - 2")
    print("70-79 OVR - 3")
    print("60-69 OVR - 4")
    print("50-59 OVR - 5")
    print("")
    print("Return    - 6")
    print("")
    storepageinput = input()
    if storepageinput == "6":
        # Return to main store menu
        storepage()
    else:
        clear()
        # Open player viewer for the selected rating range
        if storepageinput == "1":
            playerviewstore(87, 94)
        elif storepageinput == "2":
            playerviewstore(80, 86)
        elif storepageinput == "3":
            playerviewstore(70, 79)
        elif storepageinput == "4":
            playerviewstore(60, 69)
        else:
            playerviewstore(50, 59)
   
def countsaves():
    for i in range(1, 5):
        if readteamdata("inuse", i) != "yes":
            return i - 1
    return 4
         
def buildopponent():
    global edit
    # Load all players from ratings.json
    with open("ratings.json", "r") as f:
        all_players = json.load(f)
    # Load managers grouped by division from managers.json
    with open("managers.json", "r") as f:
        managers_by_div = json.load(f)
    # Division rating targets
    divisionrating = {
    1: 87,
    2: 83,
    3: 79,
    4: 75,
    5: 71,
    6: 67,
    7: 63,
    8: 59,
    9: 55,
    10: 51
    }

    # Pick random manager from this division
    divdata = next(d for d in managers_by_div if d["division"] == division)
    manager = random.choice(divdata["managers"])
    formation = manager["formation"]
    targetrating = divisionrating.get(division, 60)
    # Get formation positions (skip index 0)
    positions, _ = formationswitch(formation)
    positions = positions[1:]
    # Group players by position
    playersbyposition = {}
    for p in all_players:
        playersbyposition.setdefault(p["position"], []).append(p)
    ratingwindow = 7
    selectedplayers = []
    used_names = set()
    # Pick players near target rating per position
    for pos_info in positions:
        pos = pos_info["position"]
        candidates = playersbyposition.get(pos, [])
        filtered = [p for p in candidates if abs(p["rating"] - targetrating) <= ratingwindow]
        while not filtered and ratingwindow < 20:
            ratingwindow += 1
            filtered = [p for p in candidates if abs(p["rating"] - targetrating) <= ratingwindow]
        # Helps to avoid duplicates
        choice_pool = filtered if filtered else candidates
        player = None
        if choice_pool:
            # re-roll until unused (or give up)
            for _ in range(len(choice_pool)):
                pick = random.choice(choice_pool)
                if pick["name"] not in used_names:
                    player = pick
                    break
        if player:
            selectedplayers.append(player)
            if not player["name"].startswith("Default "):
                used_names.add(player["name"])
        else:
            selectedplayers.append({
                "name": f"Default {pos}",
                "country": "Unknown",
                "position": pos,
                "rating": targetrating
            })
    # Determine anomaly type (mutually exclusive)
    randval = random.random()
    if randval < 0.10:
        anomalytype = "onemanarmy"
    elif randval < 0.25:
        anomalytype = "slightlyabove"
    else:
        anomalytype = None
    anomalycount = random.randint(1, 3) if anomalytype else 0
    if anomalycount > 0:
        randomindices = random.sample(range(len(selectedplayers)), anomalycount)
        for i in randomindices:
            pos = selectedplayers[i]["position"]
            candidates = playersbyposition.get(pos, [])
            if anomalytype == "onemanarmy":
                maxboost = 15
            else:  # "slightlyabove"
                maxboost = 5
            for boost in range(maxboost, 0, -1):  # Try boost from max down to 1
                targetrating = selectedplayers[i]["rating"] + boost
                bettercandidates = [p for p in candidates if p["rating"] >= targetrating]
                # do not pick a name already used
                better_nodup = [p for p in bettercandidates if p["name"] not in used_names]
                if better_nodup:
                    if not selectedplayers[i]["name"].startswith("Default "):
                        used_names.discard(selectedplayers[i]["name"])
                    upgraded = random.choice(better_nodup)
                    selectedplayers[i] = upgraded
                    used_names.add(upgraded["name"])
                    # Stop once we find a suitable boosted player
                    break
    random.shuffle(selectedplayers)
    # Calculate average rating of selected players and round down
    ratings = [p["rating"] for p in selectedplayers if "rating" in p]
    averagerating = sum(ratings) / len(ratings) if ratings else 0
    # After all players are selected and optionally shuffled
    opponent_roles = opponentroles(selectedplayers, role_options, manager["rating"])
    for p in selectedplayers:
        p["role"] = opponent_roles.get(p["name"], "Unknown Role")
    # Align selectedplayers to match formationswitch order
    playerslots, _ = formationswitch(formation)
    playerslots = playerslots[1:]  # skip index 0
    ordered_players = []
    for slot in playerslots:
        expected_pos = slot["position"]
        for i, p in enumerate(selectedplayers):
            if p["position"] == expected_pos:
                ordered_players.append(p)
                selectedplayers.pop(i)
                break
        else:
            # fallback if no perfect match (shouldn't happen)
            ordered_players.append(selectedplayers.pop(0))
    # Store only player names with manager info and formation
    opponentdata = {
        "team": manager["team"],
        "manager": manager["name"], 
        "manager rating": manager["rating"],
        "manager country": manager["country"],
        "team rating": int(averagerating),
        "formation": formation,
        "players": [
            {
                "name": p["name"],
                "country": p["country"],
                "position": p["position"],
                "role": p["role"],
                "rating": p["rating"]
            } for p in ordered_players
        ],
        "tactics": {
            "directness": "Balanced",
            "tempo": "Balanced",
            "dribbling": "Balanced",
            "press": "Balanced",
            "defensive line": "Balanced",
            "defensive width": "Balanced",
            "approach": {
                "left": False,
                "middle": True,
                "right": False
            }
        }
    }
    # Write opponent team to save file under 'opponent' key
    writeteamdata(opponentdata, "opponent", edit)
    return opponentdata

def changerole(player, indexinxi):
    global edit
    squad = readteamdata("squad", edit)
    formation = readteamdata("formation", edit)
    player_slots, _ = formationswitch(formation)
    pos = player_slots[indexinxi]["position"].upper()
    roleoptions = {}
    if pos == "GK":
        roleoptions = {
            "Goalkeeper": ["Defend"]
        }
    elif pos in ["LB", "RB"]:
        roleoptions = {
            "Fullback": ["Defend", "Support", "Attack"],
            "Inverted Wingback": ["Defend", "Support", "Attack"]
        }
    elif pos == "CB":
        roleoptions = {
            "Centreback": ["Defend", "Stopper", "Cover"],
            "Ball Playing Defender": ["Defend", "Stopper", "Cover"],
            "Libero": ["Support", "Attack"]
        }
    elif pos in ["LW", "RW"]:
        roleoptions = {
            "Winger": ["Support", "Attack"],
            "Inside Forward": ["Support", "Attack"],
            "Wide Target Forward": ["Support", "Attack"],
            "Wide Playmaker": ["Support", "Attack"]
        }
    elif pos == "ST":
        roleoptions = {
            "Advanced Forward": ["Attack"],
            "Poacher": ["Attack"],
            "Target Forward": ["Support", "Attack"],
            "False Nine": ["Support"],
            "Complete Forward": ["Attack", "Support"]
        }
    elif pos == "CM":
        roleoptions = {
            "Central Midfielder": ["Defend", "Support", "Attack"],
            "Box to Box Midfielder": ["Support"],
            "Ball Winning Midfielder": ["Defend", "Support"],
            "Playmaker": ["Support"]
        }
    else:
        print("No roles available for this position")
        time.sleep(1)
        viewplayerdetails(player, indexinxi)
        return
    
    def writerole(newrole):
        squad[indexinxi - 1]["role"] = newrole
        writeteamdata(squad, "squad", edit)
        clear()
        print("")
        print(f"Role changed to: {newrole}")
        print("")
        time.sleep(1)
        # Update the in-memory player role
        player["role"] = newrole  
        viewplayerdetails(player, indexinxi)
    
    # Select role category
    while True:
        clear()
        print("")
        print("CHOOSE ROLE")
        print("")
        for i, role_cat in enumerate(roleoptions.keys(), 1):
            print(f"{role_cat} - {i}")
        print("")
        print("Return - R")
        print("")
        mysquadpageinput = input().lower()
        if mysquadpageinput.isdigit():
            mysquadpageinputnum = int(mysquadpageinput)
            if 1 <= mysquadpageinputnum <= len(roleoptions):
                selectedcat = list(roleoptions.keys())[mysquadpageinputnum - 1]
                break
        elif mysquadpageinput == "r":
            viewplayerdetails(player, indexinxi)
            return
    # Select role style
    styles = roleoptions[selectedcat]
    while True:
        clear()
        print("")
        print("CHOOSE STYLE")
        print("")
        for i, style in enumerate(styles, 1):
            print(f"{style} - {i}")
        print("")
        print("Return - R")
        print("")
        mysquadpageinput = input().lower()
        if mysquadpageinput.isdigit():
            mysquadpageinputnum = int(mysquadpageinput)
            if 1 <= mysquadpageinputnum <= len(styles):
                selectedstyle = styles[mysquadpageinputnum - 1]
                break
        elif mysquadpageinput == "r":
            return changerole(player, indexinxi)
    newrole = f"{selectedcat} ({selectedstyle})"
    writerole(newrole)

# Role to stats mapping
roleweights = {
    "Fullback": {
        "Defend": ["defending","physical"],
        "Support": ["dribbling","defending"],
        "Attack": ["pace","dribbling"]
    },
    "Inverted Wingback": {
        "Defend": ["defending","passing"],
        "Support": ["passing","dribbling","defending"],
        "Attack": ["passing","dribbling"]
    },
    "Centreback": {
        "Defend": ["defending"],
        "Stopper": ["defending","physical"],
        "Cover": ["pace","defending"]
    },
    "Ball Playing Defender": {
        "Defend": ["defending","passing"],
        "Stopper": ["defending","physical","passing"],
        "Cover": ["pace","passing","defending"]
    },
    "Libero": {
        "Support": ["defending", "passing"],
        "Attack": ["defending", "dribbling"]
    },
    "Winger": {
        "Support": ["dribbling"],
        "Attack": ["pace","dribbling"]
    },
    "Inside Forward": {
        "Support": ["dribbling","pace", "passing"],
        "Attack": ["pace","dribbling","shooting"]
    },
    "Wide Target Forward": {
        "Support": ["physical"],
        "Attack": ["physical","shooting"]
    },
    "Wide Playmaker": {
        "Support": ["passing","dribbling"],
        "Attack": ["passing","dribbling","pace"]
    },
    "Advanced Forward": { 
        "": ["pace","shooting","dribbling"] 
    },
    "Poacher": { 
        "": ["shooting"] 
    },
    "Target Forward": {
        "Support": ["physical"],
        "Attack":  ["physical","shooting"]
    },
    "False Nine": { 
        "": ["passing","dribbling","shooting"] 
    },
    "Complete Forward": {
        "Attack":  ["pace","shooting","physical"],
        "Support": ["shooting","passing","physical"]
    },
    "Central Midfielder": {
        "Defend":  ["defending","passing"],
        "Support": ["passing"],
        "Attack":  ["passing","shooting"]
    },
    "Box to Box Midfielder": { 
        "": ["passing","physical","defending","dribbling"] 
    },
    "Ball Winning Midfielder": {
        "Defend":  ["defending","physical"],
        "Support": ["defending","physical","passing"]
    },
    "Playmaker": { 
        "": ["passing","dribbling"] 
    }
}

def rolerating(playername, role):
    global roleweights
    try:
        with open("ratings.json", "r") as f:
            all_players = json.load(f)
    except Exception:
        return 0  # Could not load ratings.json
    # Find the player stats by name
    stats = {}
    for p in all_players:
        if p["name"] == playername:
            stats = p.get("stats", {})
            break
    if not stats:
        return 0  # Player or stats not found
    # Parse role into base_role and style (e.g. "Fullback" and "Support")
    if "(" in role and ")" in role:
        baserole = role.split("(")[0].strip()
        style = role.split("(")[1].strip(" )")
    else:
        baserole = role.strip()
        style = ""
    global roleweights
    # Get stats list for this role and style
    weights = []
    if baserole in roleweights:
        if style and style in roleweights[baserole]:
            weights = roleweights[baserole][style]
        elif "" in roleweights[baserole]:
            weights = roleweights[baserole][""]
        else:
            weights = next(iter(roleweights[baserole].values()))
    else:
        return 0
    # Calculate average of the selected stats
    statvalues = [stats.get(stat, 0) for stat in weights]
    if not statvalues:
        return 0
    n = len(statvalues)
    if   n <= 1: scale = 0.97  
    elif n == 2: scale = 1.00
    elif n == 3: scale = 1.02 
    elif n == 4: scale = 1.04
    elif n == 5: scale = 1.06
    else:        scale = 1.08
    return sum(statvalues) / n * scale

def opponentroles(players, role_options, manager_rating, iterations=1000):
    def weightedroleselection(rated_roles, manager_rating):
        # rated_roles: list of (role_name, role_score)
        # manager_rating: 50 (worst) .. 99 (best)
        if not rated_roles:
            return None
        # clamp manager_rating just in case
        if manager_rating < 50: manager_rating = 50
        if manager_rating > 99: manager_rating = 99
        # skill in [0,1]: 50→0 (worst), 99→1 (best)
        skill = (manager_rating - 50) / (99 - 50)
        # 1) exploration (ε): worst explores a lot, best almost never
        #    50→~0.35, 75→~0.19, 99→~0.03
        epsilon = 0.35 - 0.32 * skill
        # 2) misjudgement chance: worst sometimes prefers BAD roles on purpose
        #    50→~0.45, 75→~0.15, 99→~0.00
        p_bad = 0.45 * (1.0 - skill) ** 0.8
        # 3) evaluation noise (std in rating points): worst sees noisy differences
        #    50→~8,  99→~0
        noise_std = 8.0 * (1.0 - skill)
        # 4) softmax temperature (peakiness): worst flat, best peaky
        #    50→~1.6, 99→~0.35
        T = 1.6 - 1.25 * skill
        if T < 0.15: T = 0.15
        # build noisy perceived scores
        perceived = []
        for role, score in rated_roles:
            s = float(score) + random.gauss(0.0, noise_std)
            perceived.append((role, s))
        # sometimes intentionally bias toward worse roles for bad managers
        direction = -1.0 if random.random() < p_bad else 1.0
        # softmax over perceived scores (with direction and temperature)
        logits = [direction * s / T for _, s in perceived]
        m = max(logits)
        exps = [math.exp(x - m) for x in logits]
        Z = sum(exps) or 1.0
        probs = [e / Z for e in exps]
        # ε-greedy exploration: worst samples from bottom half, best from top half
        if random.random() < epsilon and len(rated_roles) > 1:
            sorted_true = sorted(rated_roles, key=lambda x: x[1], reverse=True)
            half = max(1, len(sorted_true) // 2)
            pool = sorted_true[half:] if skill < 0.5 else sorted_true[:half]
            return random.choice(pool)[0]
        # exploit: sample by softmax probs
        r = random.random()
        acc = 0.0
        for (role, _), p in zip(rated_roles, probs):
            acc += p
            if r <= acc:
                return role
        return rated_roles[-1][0]
    # --- Initial assignment using weighted role logic ---
    assignment = {}
    for p in players:
        pos = p['position']
        possible_roles = role_options.get(pos, ["Default Role"])
        rated_roles = [(role, rolerating(p['name'], role)) for role in possible_roles]
        assignment[p['name']] = weightedroleselection(rated_roles, manager_rating)

    # --- Team rating function ---
    def totalteamrating(assign):
        return sum(rolerating(p['name'], assign[p['name']]) for p in players)
    # --- Optional refinement via simulated annealing-like search ---
    mr = max(50, min(99, manager_rating))
    skill = (mr - 50) / (99 - 50)
    iters = max(50, int(800 * skill))
    current_rating = totalteamrating(assignment)
    for _ in range(iters):
        player = random.choice(players)
        pos = player['position']
        current_role = assignment[player['name']]
        possible_roles = role_options.get(pos, ["Default Role"])
        other_roles = [r for r in possible_roles if r != current_role]
        if not other_roles:
            continue
        new_role = random.choice(other_roles)
        new_assignment = assignment.copy()
        new_assignment[player['name']] = new_role
        new_rating = totalteamrating(new_assignment)
        acceptance_prob = 0.25 * (1.0 - skill)
        if new_rating > current_rating:
            assignment = new_assignment
            current_rating = new_rating
        elif random.random() < acceptance_prob:
            assignment = new_assignment
            current_rating = new_rating
    return assignment

def playmatchpage():
    clear()
    print("")
    print("The match is beginning in a few seconds...")
    time.sleep(3)
    clear()
    print("")
    print("GAME")
    print("")
    playpageinput = input("Press enter to start the game")
    clear()
    print("")
    print("GAME")
    print("")
    print("The match has started!")
    time.sleep(1)
    clear()
    print("")
    matchengine()

def get_role_attributes(role_str):
    # Define the roleweights dictionary inside the function (or import from global)
    global roleweights
    if not role_str:
        return []
    # Parse role string (e.g., "Fullback (Support)")
    if "(" in role_str and ")" in role_str:
        base = role_str.split("(")[0].strip()
        style = role_str.split("(")[1].strip(" )")
    else:
        base = role_str.strip()
        style = ""
    # Find the correct attributes
    if base not in roleweights:
        return []
    role_dict = roleweights[base]

    if style in role_dict:
        return role_dict[style]
    elif "" in role_dict:
        return role_dict[""]
    else:
        # fallback to first available key if style not found
        return next(iter(role_dict.values()))
    
def matchengine():
    clear()
    # Configuration
    chancefrequency = 10      # Lower = more chances (was 33)
    xgbase = 0.3              # Starting expected goals (was 0.5)
    xgmultiplier = 0.0025     # How much rating diff influences xG (was 0.004)
    xgdifficulty = 1       # Multiplier to make goals harder (was 0.75)
    maxmidfieldrating = 100       # Max possible midfielder rating
    ratingdrift = 30              # Random +/- rating swing
    distancefactorrange = (0.4, 2.0)
    pressurefactorrange = (0.6, 1.2)
    chaosfactorrange = (0.75, 1.3)
    xgbasevalue = 0.25         # Baseline xG for any chance
    xgscalingfactor = 0.01     # Multiplier for how much the rating diff affects xG
    xgbiasrange = (-0.08, 0.15)   # Additional randomness added to xG
    xgmin = 0.05
    xgmax = 0.95
    # Load your team
    formation = readteamdata("formation", edit)
    playerslots, _ = formationswitch(formation)
    yoursquad = readteamdata("squad", edit)
    yourteamname = readteamdata("team", edit)
    # Load opponent team
    opponentdata = readteamdata("opponent", edit)
    oppsquad = opponentdata["players"]
    oppformation = opponentdata["formation"]
    oppslots, _ = formationswitch(oppformation)
    opponentname = opponentdata["team"]
    
    
    
    
    outfield = yoursquad[:11]
    yourteam = [p for p in outfield if p["position"] != "GK"]
    outfield = oppsquad[:11]
    oppteam = [p for p in outfield if p["position"] != "GK"]
    # Define the six core attributes once
    attributes = ["pace", "shooting", "passing", "dribbling", "defending", "physical"]
    # Initialise total counters for both teams
    your_totals = {attr: 0 for attr in attributes}
    opp_totals = {attr: 0 for attr in attributes}
    # Loop through yourteam
    for player in yourteam:
        role = player.get("role", "")
        stats = player.get("stats", {})
        used_attrs = get_role_attributes(role)  # returns list of relevant attributes for this role
        for attr in used_attrs:
            if attr in attributes:  # double check it's a tracked attribute
                your_totals[attr] += stats.get(attr, 0)
    # Loop through oppteam
    for player in oppteam:
        role = player.get("role", "")
        stats = player.get("stats", {})
        used_attrs = get_role_attributes(role)
        for attr in used_attrs:
            if attr in attributes:
                opp_totals[attr] += stats.get(attr, 0)
    # Store them in variables if you want individual ones
    totalpace_your = your_totals["pace"]
    totalshooting_your = your_totals["shooting"]
    totalpassing_your = your_totals["passing"]
    totaldribbling_your = your_totals["dribbling"]
    totaldefending_your = your_totals["defending"]
    totalphysical_your = your_totals["physical"]
    totalpace_opp = opp_totals["pace"]
    totalshooting_opp = opp_totals["shooting"]
    totalpassing_opp = opp_totals["passing"]
    totaldribbling_opp = opp_totals["dribbling"]
    totaldefending_opp = opp_totals["defending"]
    totalphysical_opp = opp_totals["physical"]
    
        
    
            
    # Indexes for each position group
    yourdefenderindex = [i for i in range(1, 12) if playerslots[i]["position"] in ["LB", "CB", "RB", "GK"]]
    oppdefenderindex = [i for i in range(1, 12) if oppslots[i]["position"] in ["LB", "CB", "RB", "GK"]]
    yourmidfieldindex = [i for i in range(1, 12) if playerslots[i]["position"] == "CM"]
    oppmidfieldindex = [i for i in range(1, 12) if oppslots[i]["position"] == "CM"]
    yourattackerindex = [i for i in range(1, 12) if playerslots[i]["position"] in ["ST", "LW", "RW"]]
    oppattackerindex = [i for i in range(1, 12) if oppslots[i]["position"] in ["ST", "LW", "RW"]]
    # Match stats
    score = {yourteamname: 0, opponentname: 0}
    shots = {yourteamname: 0, opponentname: 0}
    xg_total = {yourteamname: 0.0, opponentname: 0.0}
    matchlog = []
    global matchratings
    matchratings = {}  # Store player ratings
    for p in yoursquad + oppsquad:
        matchratings[p["name"]] = 6.0
    for matchmin in range(91):
        generatechance = random.randint(1, chancefrequency)
        chancehappened = False
        p = None
        midfielderrating = 0
        attackingteam = None
        if generatechance == 1 and yourmidfieldindex:
            idx = random.choice(yourmidfieldindex)
            p = yoursquad[idx - 1]
            _, midfielderrating = chemistry(p["name"])
            attackingteam = yourteamname
            chancehappened = True
        elif generatechance == 10 and oppmidfieldindex:
            idx = random.choice(oppmidfieldindex)
            p = oppsquad[idx - 1]
            _, midfielderrating = chemistry(p["name"], opponent=True)
            attackingteam = opponentname
            chancehappened = True
        # Process the chance
        if chancehappened:
            print(f"{matchmin}': {p['name']} on the ball for {attackingteam}...")
            time.sleep(1.5)
            if random.randint(1, 130) <= midfielderrating:
                print(f"{matchmin}': {p['name']} creates a chance...")
                matchratings[p["name"]] += 0.5
                time.sleep(1.5)
                if attackingteam == yourteamname:
                    attacker = yoursquad[random.choice(yourattackerindex) - 1]
                    _, attackerrating = chemistry(attacker["name"])
                    defender = oppsquad[random.choice(oppdefenderindex) - 1]
                    _, defenderrating = chemistry(defender["name"], opponent=True)
                    defender_slot = oppslots
                    squad_ref = oppsquad
                else:
                    attacker = oppsquad[random.choice(oppattackerindex) - 1]
                    _, attackerrating = chemistry(attacker["name"], opponent=True)
                    defender = yoursquad[random.choice(yourdefenderindex) - 1]
                    _, defenderrating = chemistry(defender["name"])
                    defender_slot = playerslots
                    squad_ref = yoursquad
                # xG calculation
                # Add random modifier to simulate shot context
                ratingdiff = (attackerrating - defenderrating) + random.randint(-ratingdrift, ratingdrift)
                # Midfielder quality remains a factor
                midfielderfactor = midfielderrating / maxmidfieldrating
                # Distance/angle/pressure simulation
                distancefactor = random.uniform(*distancefactorrange) # randomly affects xG quality
                pressurefactor = random.uniform(*pressurefactorrange)  # higher defender rating = more pressure
                chaosfactor = random.uniform(*chaosfactorrange)  # Just to shake it up a bit
                # Compute xG using multiple influences
                xg = xgbasevalue + xgscalingfactor * ratingdiff * midfielderfactor * distancefactor * pressurefactor * chaosfactor
                xg += random.uniform(*xgbiasrange)
                # Clamp xG between 0.05 and 0.95
                xg = max(xgmin, min(xgmax, xg))
                xg_total[attackingteam] += xg
                shots[attackingteam] += 1
                print(f"{matchmin}': {attacker['name']} shoots...")
                time.sleep(1.5)
                # Figure out defender's position
                pos = "DEF"
                for i in range(1, 12):
                    if squad_ref[i - 1]["name"] == defender["name"]:
                        pos = defender_slot[i]["position"]
                        break
                # Outcome
                if random.random() <= xg * xgdifficulty:
                    msg = f"{matchmin}': GOAL FOR {attackingteam.upper()} SCORED BY {attacker['name'].upper()}!!! (xG: {xg:.2f})"
                    matchratings[attacker["name"]] += 2*(1-(round(xg, 1)))
                    matchratings[defender["name"]] -= 2*round(xg, 1)
                    score[attackingteam] += 1
                else:
                    saveword = "SAVED" if pos == "GK" else "BLOCKED"
                    msg = f"{matchmin}': {saveword.upper()} BY {defender['name'].upper()} TO DENY {attackingteam.upper()}! (xG: {xg:.2f})"
                    matchratings[attacker["name"]] -= 2*(round(xg, 1))
                    matchratings[defender["name"]] += 2*round(xg, 1)
                print(msg)
                matchlog.append(msg)
                time.sleep(1.5)
            else:
                print(f"{matchmin}': Dispossessed")
                matchratings[p["name"]] -= 0.5
                time.sleep(1.5)
        # Scoreboard
        time.sleep(0.2)
        clear()
        print("")
        print("GAME")
        print("")
        print(f"Minute: {matchmin}")
        print(f"{yourteamname} {score[yourteamname]} - {score[opponentname]} {opponentname}\n")
        print(f"Shots: {shots[yourteamname]} - {shots[opponentname]}")
        print(f"xG:    {xg_total[yourteamname]:.2f} - {xg_total[opponentname]:.2f}\n")
        print("Match Events:")
        for event in matchlog[-5:]:
            print(event)
        print("")
    # Clamp ratings between 1 and 10
    for name in matchratings:
        matchratings[name] = max(1, min(10, matchratings[name]))
    print("FULL TIME")
    time.sleep(1)
    fulltime(yourteamname, opponentname, score, shots, xg_total, matchlog, yoursquad, oppsquad)

def fulltime(yourteamname, opponentname, score, shots, xg_total, matchlog, yoursquad, oppsquad):
    clear()
    print("")
    print("FULL TIME")
    print("")
    print(f"{yourteamname} {score[yourteamname]} - {score[opponentname]} {opponentname}")
    print("\nMatch Statistics:")
    print(f"Shots: {shots[yourteamname]} - {shots[opponentname]}")
    print(f"xG:    {xg_total[yourteamname]:.2f} - {xg_total[opponentname]:.2f}")
    print("\nMatch Events (Key Moments):")
    for log in matchlog:
        if "GOAL" in log or "SAVED" in log or "BLOCKED" in log:
            print(log)
    print("")
    print("View your player ratings     - 1")
    print("View opponent player ratings - 2")
    print("Continue                     - 3")
    print("")
    playpageinput = input()
    if playpageinput == "1":
        showratings(score, shots, xg_total, matchlog, matchratings, yourteamname, opponentname, yoursquad, oppsquad)
    elif playpageinput == "2":
       showratings(score, shots, xg_total, matchlog, matchratings, yourteamname, opponentname, yoursquad, oppsquad, opponent = True)
    elif playpageinput == "3":
        clear()
        print("")
        print("REWARDS")
        print("")
        time.sleep(0.1)
        global points, coins, division, gamesremaining
        yourratings = [p["rating"] for p in yoursquad[:11]]
        oppratings = [p["rating"] for p in oppsquad[:11]]
        yourteamrating = sum(yourratings) / 11
        oppteamrating = sum(oppratings) / 11
        goalsscored = score[yourteamname]
        goalsconceded = score[opponentname]
        earntcoins = 0
        gamesremaining -= 1
        if goalsscored > goalsconceded:
            points += 3
            if yourteamrating > oppteamrating:
                earntcoins = 100
            elif yourteamrating == oppteamrating:
                earntcoins = 150
            else:
                earntcoins = 200
        elif goalsscored == goalsconceded:
            points += 1
            if yourteamrating > oppteamrating:
                earntcoins = 25
            elif yourteamrating == oppteamrating:
                earntcoins = 50
            else:
                earntcoins = 75
        print(f"Match result: +{earntcoins}")
        time.sleep(0.1)
        bonus = goalsscored * 10
        penalty = goalsconceded * 10
        print(f"Goals scored: +{bonus}")
        time.sleep(0.1)
        print(f"Goals conceded: -{penalty}")
        time.sleep(0.1)
        earntcoins = earntcoins + bonus - penalty
        print(f"Total coins earnt: {earntcoins}")
        time.sleep(0.1)
        coins += earntcoins
        if coins < 0:
            coins = 0
        writeteamdata(str(gamesremaining), "gamesremaining", edit)    
        writeteamdata(str(coins), "coins", edit)
        writeteamdata(str(points), "points", edit)
        print("")
        print("Continue")
        print("")
        removeopponent(edit)
        playpageinput = input()
        if gamesremaining == 0:
            clear()
            print("")
            print("REWARDS")
            print("")
            time.sleep(1)
            relegationthreshhold = 7
            promotionthreshhold = 14
            titlethreshhold = 23
            if points < relegationthreshhold:
                if division >= 9:
                    division += 1
                    print(f"You have been relegated to Division {division}")
                    time.sleep(0.1)
                else:
                    print(f"You have stayed in Division {division}")
                    time.sleep(0.1)
                endofseasonrewards = 0
            elif points >= titlethreshhold:
                print("You have won the title!")
                time.sleep(0.1)
                if division > 1:
                    division -= 1
                    print(f"You have been promoted to Division {division}")
                    time.sleep(0.1)
                endofseasonrewards = {1: 3250, 2: 3000, 3: 2750, 4: 2500, 5: 2250, 6: 2000, 7: 1750, 8: 1500, 9: 1250}.get(division, 1000)
            elif points >= promotionthreshhold:
                if division > 1:
                    division -= 1
                    print(f"You have been promoted to Division {division}")
                    time.sleep(0.1)
                else:
                    print(f"You have stayed in Division {division}")
                    time.sleep(0.1)
                endofseasonrewards = 1000
            else:
                print(f"You have stayed in Division {division}")
                time.sleep(0.1)
                endofseasonrewards = 500
            print(f"Extra coins earnt: +{endofseasonrewards}")
            time.sleep(0.1)
            gamesremaining = 10
            points = 0
            coins += endofseasonrewards
            writeteamdata(str(division), "division", edit)
            writeteamdata(str(gamesremaining), "gamesremaining", edit)
            writeteamdata(str(points), "points", edit)
            writeteamdata(str(coins), "coins", edit)
            print("")
            print("Continue")
            print("")
            playpageinput = input()    
        playpage()

def showratings(score, shots, xg_total, matchlog, matchratings, yourteamname, opponentname, yoursquad, oppsquad, opponent = False):
    clear()
    if opponent:
        print(f"\n{opponentname.upper()} PLAYER RATINGS:")
        print("")
        for p in oppsquad[:11]:
            rating = matchratings.get(p["name"], 6.0)
            print(f"{p['name']}: {rating:.1f}/10")
    else:
        print(f"\n{yourteamname.upper()} PLAYER RATINGS:")
        print("")
        for p in yoursquad[:11]:
            rating = matchratings.get(p["name"], 6.0)
            print(f"{p['name']}: {rating:.1f}/10")
    print("")
    print("Return - R")
    playpageinput = input()
    fulltime(yourteamname, opponentname, score, shots, xg_total, matchlog, yoursquad, oppsquad)

def viewopponentplayers(opponent):
    squad = opponent["players"]
    formation = opponent["formation"]
    opponentteam = opponent.get("team", "Opponent").upper()
    playerslots, _ = formationswitch(formation)
    # Load all player data with stats
    with open("ratings.json", "r") as f:
        all_players = json.load(f)
    while True:
        clear()
        print("")
        print(f"{opponentteam} PLAYERS")
        print("")
        print(f"Team Chemistry: {teamchemistry(opponent = True)} / 100")
        for i, p in enumerate(squad, 1):
            pos = playerslots[i]["position"]
            print(f"{i}. {pos:1} - {p['name']} ({p['rating']} OVR, {p['country']})")
        print("")
        print("Return - R")
        print("")
        playpageinput = input().lower()
        if playpageinput == "r":
            matchpage()
        elif playpageinput.isdigit():
            index = int(playpageinput)
            if 1 <= index <= len(squad):
                player = squad[index - 1]
                chemlevel, _ = chemistry(player["name"], opponent=True)
                clear()
                print("")
                print(f"{opponentteam} PLAYER DETAILS")
                print("")
                print(f"Name: {player['name']}")
                print(f"Country: {player['country']}")
                print(f"Position: {player['position']}")
                print(f"Role: {player['role']}")
                print(f"Base Rating: {player['rating']}")
                print(f"Chemistry Level: {chemlevel}/10")
                # Find full player data in ratings.json
                try:
                    with open("ratings.json", "r") as f:
                        ratings_data = json.load(f)
                    name_to_full = {p["name"]: p for p in ratings_data}
                    full_player = name_to_full.get(player["name"], {})
                    stats = full_player.get("stats", None)
                    if stats:
                        print("Stats:")
                        print(f"  pace:      {stats.get('pace', 'N/A')}")
                        print(f"  shooting:  {stats.get('shooting', 'N/A')}")
                        print(f"  passing:   {stats.get('passing', 'N/A')}")
                        print(f"  dribbling: {stats.get('dribbling', 'N/A')}")
                        print(f"  defending: {stats.get('defending', 'N/A')}")
                        print(f"  physical:  {stats.get('physical', 'N/A')}")
                    else:
                        print("")
                        print("Stats: Not available")
                except Exception:
                    print("")
                    print("Stats: Error loading ratings.json")
                print("")
                print("Return - R")
                print("")
                playpageinput = input()
                if playpageinput == "r":
                    viewopponentplayers(opponent)

def matchpage():
    try:
        opponent = readteamdata("opponent", edit)
    except KeyError:
        clear()
        print("")
        print("MATCH")
        print("")
        print("Generating opponent... ")
        print("")
        opponent = buildopponent()
    clear()
    print("")
    print("MATCH")
    print("")
    print(f"Upcoming opponent: {opponent['team']}")
    print(f"Manager: {opponent['manager']} - {opponent['manager rating']} OVR")
    print(f"Team rating: {opponent['team rating']} OVR")
    print(f"Formation: {opponent['formation']}")
    print("")
    print("Play match            - 1")
    print("View opponent players - 2")
    print("Return                - 3")
    print("")
    playpageinput = input()
    if playpageinput == "1":
        playmatchpage()
    elif playpageinput == "2":
        viewopponentplayers(opponent)
    elif playpageinput == "3":
        playpage()

def startprogram():
    # Main entry menu for the game
    clear()
    print("")
    print("PACK TO PITCH")
    time.sleep(0.5)
    print("")
    print("Start New Game - 1")
    print("Load Save Game - 2")
    print("Tutorial       - 3")
    print("Exit           - 4")
    print("")
    startprograminput = input()
    if startprograminput == "1":
        # Create a new game session
        startnewgame()
    elif startprograminput == "2":
        # Load an existing save file
        loadsavegame()
    elif startprograminput == "4":
        # Exit the game
        clear()
        print("")
        print("Exiting...")
        print("")
        time.sleep(1)
        clear()
        sys.exit()
        
def deletesavegame():
    global edit
    clear()
    print("")
    print("DELETE")
    print("")
    for i in range(1, edit + 1):
        print("Save name: " + readteamdata("team", i) + " - " + str(i))
    print("")
    print("Return - " + str(edit+1))
    print("")
    loadsavegameinput = input().strip()
    if not loadsavegameinput.isdigit():
        invalid(deletesavegame)
        return
    idx = int(loadsavegameinput)
    if idx == edit + 1:
        loadsavegame()
        return
    elif not (1 <= idx <= edit):
        invalid(deletesavegame)
        return
    # Shift save data up by one from idx to 3
    for i in range(idx, 4):
        for field in ["inuse", "team", "manager", "manager country", "coins", "division", "gamesremaining", "points", "squad", "formation"]:
            try:
                next_data = readteamdata(field, i + 1)
                writeteamdata(next_data, field, i)
            except:
                pass  # If data doesn't exist (e.g., on slot 4), skip
    # Overwrite slot 4 with default empty save
    last = 4
    defaultsquad = [
        {"name": "Jack Thompson", "country": "England", "position": "GK", "rating": 50, "role": "Goalkeeper"},	
        {"name": "Liam O'Connor", "country": "England", "position": "LB", "rating": 51, "role": "Fullback (Support)"},
        {"name": "Ben Harris", "country": "England", "position": "CB", "rating": 52, "role": "Centreback (Defend)"},
        {"name": "Charlie Moore", "country": "England", "position": "CB", "rating": 50, "role": "Centreback (Defend)"},
        {"name": "Oscar Walker", "country": "England", "position": "RB", "rating": 51, "role": "Fullback (Support)"},
        {"name": "George Wright", "country": "England", "position": "LW", "rating": 52, "role": "Winger (Support)"},
        {"name": "Harvey Cooper", "country": "England", "position": "CM", "rating": 50, "role": "Central Midfielder (Support)"},
        {"name": "Sam Allen", "country": "England", "position": "CM", "rating": 51, "role": "Central Midfielder (Support)"},
        {"name": "Luke Richardson", "country": "England", "position": "RW", "rating": 52, "role": "Winger (Support)"},
        {"name": "Tommy Evans", "country": "England", "position": "ST", "rating": 50, "role": "Advanced Forward (Attack)"},
        {"name": "Joe Mitchell", "country": "England", "position": "ST", "rating": 51, "role": "Advanced Forward (Attack)"}
    ]
    defaulttactics = {
        "directness": "Balanced",
        "tempo": "Balanced",
        "dribbling": "Balanced",
        "press": "Balanced",
        "approach": {
            "left": False,
            "middle": True,
            "right": False
        }
    }
    # Write default data
    writeteamdata("no", "inuse", last)
    writeteamdata("MyTeam", "team", last)
    writeteamdata("YourManagerName", "manager", last)
    writeteamdata("England", "manager country", last)
    writeteamdata("1000", "coins", last)
    writeteamdata("10", "division", last)
    writeteamdata("10", "gamesremaining", last)
    writeteamdata("0", "points", last)
    writeteamdata("4-4-2", "formation", last)
    writeteamdata(defaultsquad, "squad", last)
    writeteamdata(defaulttactics, "tactics", last)
    # Remove leftover keys like "opponent" from the last slot
    filepath = f"teamdata{last}.json"
    with open(filepath, "r") as f:
        data = json.load(f)
    data.pop("opponent", None)
    with open(filepath, "w") as f:
        json.dump(data, f)
    edit -= 1
    clear()
    time.sleep(1)
    print("")
    print("Deleting...")
    print("")
    time.sleep(2)
    clear()
    print("")
    print("Game save deleted")
    print("")
    time.sleep(1)
    loadsavegame()

def loadsavegame():
    clear()
    print("")
    print("LOAD SAVE GAME")
    print("")
    global edit
    edit = countsaves()
    # Check if slot 1 is unused → assume no saves at all
    if readteamdata("inuse", 1) == "no":
        print("No save games found")
        print("")
        print("Continue")
        print("")
        loadsavegameinput = input()
        startprogram()
        return
    # Show all existing saves, stop at first empty one
    for i in range(1, 5):
        if readteamdata("inuse", i) == "yes":
            print("Save name: " + readteamdata("team", i) + " - " + str(i))
        else:
            break
    print("")
    print("Delete save - D")
    print("Return      - R")
    print("")
    loadsavegameinput = input().lower()
    global teamname, coins, division, gamesremaining, points, managername, managercountry
    if loadsavegameinput == "d":
        deletesavegame()
    elif loadsavegameinput == "r":
        startprogram()
    elif loadsavegameinput.isdigit() and 1 <= int(loadsavegameinput) <= 4:
        edit = int(loadsavegameinput)
        teamname = readteamdata("team", edit)
        coins = int(readteamdata("coins", edit))
        division = int(readteamdata("division", edit))
        gamesremaining = int(readteamdata("gamesremaining", edit))
        points = int(readteamdata("points", edit))
        managername = readteamdata("manager", edit)
        managercountry = readteamdata("manager country", edit)
        clear()
        print("")
        print("Loading...")
        print("")
        time.sleep(1)
        homepage()
    else:
        invalid(loadsavegame)

def startnewgame():
    clear()
    print("")
    print("START NEW GAME")
    print("")
    global teamname, managername, managercountry
    # Ask the user to name their new team
    teamname = input("Enter your team name: ")
    # Ask for manager name
    managername = input("Enter your manager's name: ").strip()
    # Extract available countries from ratings.json
    with open("ratings.json", "r") as f:
        playerdata = json.load(f)
    availablecountries = sorted(set(p["country"] for p in playerdata))
    # Ask user to choose a country
    print("Available countries:")
    for i, c in enumerate(availablecountries, 1):
        print(f"{i}. {c}")
    print("")
    while True:
        choice = input("Choose your manager's country by number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(availablecountries):
            managercountry = availablecountries[int(choice) - 1]
            break
        else:
            print("Invalid choice. Try again.")
    time.sleep(0.3)
    print("")
    print("Creating game session.. ")
    global edit
    # Find the first available save slot
    for slot in range(1, 5):
        if readteamdata("inuse", slot) == "no":
            edit = slot
            # Create default starter squad
            defaultsquad = [
                {"name": "Jack Thompson", "country": "England", "position": "GK", "rating": 50, "role": "Goalkeeper"},	
                {"name": "Liam O'Connor", "country": "England", "position": "LB", "rating": 51, "role": "Fullback (Support)"},
                {"name": "Ben Harris", "country": "England", "position": "CB", "rating": 52, "role": "Centreback (Defend)"},
                {"name": "Charlie Moore", "country": "England", "position": "CB", "rating": 50, "role": "Centreback (Defend)"},
                {"name": "Oscar Walker", "country": "England", "position": "RB", "rating": 51, "role": "Fullback (Support)"},
                {"name": "George Wright", "country": "England", "position": "LW", "rating": 52, "role": "Winger (Support)"},
                {"name": "Harvey Cooper", "country": "England", "position": "CM", "rating": 50, "role": "Central Midfielder (Support)"},
                {"name": "Sam Allen", "country": "England", "position": "CM", "rating": 51, "role": "Central Midfielder (Support)"},
                {"name": "Luke Richardson", "country": "England", "position": "RW", "rating": 52, "role": "Winger (Support)"},
                {"name": "Tommy Evans", "country": "England", "position": "ST", "rating": 50, "role": "Advanced Forward (Attack)"},
                {"name": "Joe Mitchell", "country": "England", "position": "ST", "rating": 51, "role": "Advanced Forward (Attack)"}
            ]
            # Default tactics
            defaulttactics = {
                "directness": "Balanced",
                "tempo": "Balanced",
                "dribbling": "Balanced",
                "press": "Balanced",
                "approach": {
                    "left": False,
                    "middle": True,
                    "right": False
                }
            }
            # Write default data to the save file
            writeteamdata("yes", "inuse", edit)
            writeteamdata(teamname, "team", edit)
            writeteamdata("1000", "coins", edit)
            writeteamdata("10", "division", edit)
            writeteamdata("10", "gamesremaining", edit)
            writeteamdata("0", "points", edit)
            writeteamdata(managername, "manager", edit)
            writeteamdata(managercountry, "manager country", edit)
            writeteamdata("4-4-2", "formation", edit)
            writeteamdata(defaultsquad, "squad", edit)
            writeteamdata(defaulttactics, "tactics", edit)
            break
    else:
        # If no free slots, return to menu
        clear()
        print("")
        print("START NEW GAME")
        print("")
        print("Maximum of 4 game slots reached")
        print("")
        time.sleep(2)
        startprogram()
    global coins, division, gamesremaining, points
    # Set initial coin balance for session use
    coins = int(readteamdata("coins", edit))
    division = int(readteamdata("division", edit))
    gamesremaining = int(readteamdata("gamesremaining", edit))
    points = int(readteamdata("points", edit))
    time.sleep(2)
    clear()
    print("Game session created")
    print("")
    time.sleep(1)
    homepage()

def homepage():
    global teamname
    clear()
    print("")
    # Display the main menu after loading or creating a team
    print("HOME - " + teamname)
    print("")
    print("Play     - 1")
    print("Store    - 2")
    print("My Squad - 3")
    print("Settings - 4")
    print("Exit     - 5")
    print("")
    homepageinput = input()
    if homepageinput == "1":
        # Open the play screen
        playpage()
    elif homepageinput == "2":
        # Go to the store to buy packs
        storepage() 
    elif homepageinput == "3":
        # Open squad management screen
        mysquadpage(homepage)
    elif homepageinput == "5":
        # Return to main menu (start screen)
        clear()
        print("")
        print("Exiting...")
        print("")
        time.sleep(1)
        startprogram()
    else:
        # Handle invalid menu choice
        invalid(homepage)

def playpage():
    clear()
    print("")
    print("PLAY")
    print("")
    print("Division " + str(division))
    print("")
    if division < 10:
        print("Relegation:     7 points")
    if division > 1:
        print("Promotion:      14 points")
    print("Title:          23 points")
    print("Current points: " + str(points) + " points")
    print("Games remaining: " + str(gamesremaining) + " games")
    print("")
    print("Go to match                  - 1")
    print("View all teams in the league - 2")
    print("Team management              - 3")
    print("Return                       - 4")
    print("")
    playpageinput = input()
    if playpageinput == "1":
        matchpage()
    if playpageinput == "3":
        mysquadpage(playpage)
    elif playpageinput == "4":
        homepage()

def storepage():
    global coins
    clear()
    print("")
    print("STORE")
    print("")
    print("Coins: " + str(coins))
    print("")
    print("Regular pack - 300 coins  - 1")
    print("Prime pack - 1000 coins   - 2")
    print("Premium pack - 1500 coins - 3")
    print("View all possible players - 4")
    print("Return                    - 5")
    print("")
    f = open("ratings.json", "r")
    players = json.load(f)
    f.close()
    # Categorise players into rarity groups based on rating
    raritygroups = {
        "common": [],
        "uncommon": [],
        "rare": [],
        "epic": [],
        "legendary": []
    }
    for p in players:
        r = p["rating"]
        if r <= 64:
            raritygroups["common"].append(p)
        elif r <= 74:
            raritygroups["uncommon"].append(p)
        elif r <= 82:
            raritygroups["rare"].append(p)
        elif r <= 87:
            raritygroups["epic"].append(p)
        else:
            raritygroups["legendary"].append(p)
    storepageinput = input()
    if storepageinput == "5":
        # Return to the homepage
        homepage()
    elif storepageinput in ["1", "2", "3"]:
        # Handle pack selection and apply corresponding coin cost and rarity weights
        if storepageinput == "1":
            invalidpack(300)
            weights = {"common": 75, "uncommon": 20, "rare": 4, "epic": 1, "legendary": 0}
            coins -= 300
            writeteamdata(str(coins), "coins", edit)
        elif storepageinput == "2":
            invalidpack(1000)
            weights = {"common": 30, "uncommon": 40, "rare": 18, "epic": 9, "legendary": 3}
            coins -= 1000
            writeteamdata(str(coins), "coins", edit)
        elif storepageinput == "3":
            invalidpack(1500)
            weights = {"common": 15, "uncommon": 40, "rare": 25, "epic": 15, "legendary": 5}
            coins -= 1500
            writeteamdata(str(coins), "coins", edit)
        # Build weighted rarity pool for random selection
        raritypool = []
        for rarity, weight in weights.items():
            raritypool.extend([rarity] * weight)
        selectedrarity = random.choice(raritypool)
        candidates = raritygroups[selectedrarity]
        selectedplayer = random.choice(candidates)
        clear()
        print("")
        print("STORE")
        time.sleep(1)
        print("")
        print("Loading...")
        print("")
        time.sleep(3)
        # Display player details from pack
        print("Country - " + selectedplayer["country"])
        time.sleep(1)
        print("Position - " + selectedplayer["position"])
        time.sleep(1)
        print(str(selectedplayer["rating"]) + " OVR")
        time.sleep(1)
        print("Name - " + selectedplayer["name"])
        print("")
        squad = readteamdata("squad", edit)
        # Check if player is already owned
        alreadyowned = any(p["name"] == selectedplayer["name"] for p in squad)
        if not alreadyowned:
            # Add new player to squad
            newplayer = {
                "name": selectedplayer["name"],
                "country": selectedplayer["country"],
                "position": selectedplayer["position"],
                "rating": selectedplayer["rating"]
            }
            squad.append(newplayer)
            writeteamdata(squad, "squad", edit)
            time.sleep(2)
        else:
            print("You already own this player")
            time.sleep(0.5)
            print("Player will be quicksold for " + str(quicksell(selectedplayer['rating'])) + " coins")
            print("")
            coins += quicksell(selectedplayer['rating'])
            writeteamdata(str(coins), "coins", edit)
        storepageinput = input("Continue")
        storepage()
    else:
        # View all players by rating category
        viewallplayerspage()

def viewplayerdetails(player, indexinxi):
    # Clears the screen and shows details of a selected player in the Starting XI
    clear()
    print("")
    print("PLAYER INFO")
    print("")
    # Display the player's basic information
    print(f"Name: {player['name']}")
    print(f"Country: {player['country']}")
    print(f"Position: {player['position']}")
    # Display role if available
    role = player.get("role", "No role assigned")
    print(f"Role: {role}")
    print(f"Rating: {player['rating']}")
    # Get chemistry level (ignore final rating here)
    chemlevel, _ = chemistry(player["name"])
    print(f"Chemistry Level: {chemlevel}/10")
    # Try to load full stats from ratings.json
    try:
        with open("ratings.json", "r") as f:
            ratings_data = json.load(f)
        # Map player names to their full data
        name_to_full = {p["name"]: p for p in ratings_data}
        full_player = name_to_full.get(player["name"], {})
        # Display stats if available
        if "stats" in full_player:
            print("Stats:")
            for stat, val in full_player["stats"].items():
                print(f"  {stat}: {val}")
        else:
            print("Stats: Not available")
    except Exception:
        print("Stats: Error loading ratings.json")
    print("")
    # Offer options to swap the player or return to the squad menu
    print("Quicksell for " + str(quicksell(player['rating'])) + " coins - Q")
    print("Change role - C")
    print("Swap Player - S")
    print("")
    print("Return      - R")
    print("")
    mysquadpageinput = input().lower()
    if mysquadpageinput == "s":
        # Go to the swap player menu with the current player
        swapplayermenu(player, indexinxi)
    elif mysquadpageinput == "r":
        # Return to the My Squad page
        mysquadpage(currentreturncallback)
    elif mysquadpageinput == "q":
        quicksellplayer(player)
        mysquadpage(currentreturncallback)
    elif mysquadpageinput == "c":
        changerole(player, indexinxi)
    else:
        # Handle invalid input
        invalid(lambda: viewplayerdetails(player, indexinxi))

def swapplayermenu(currentplayer, indexinxi):
    # Get the full squad and exclude the current player from the list of swappable players
    squad = readteamdata("squad", edit)
    owned = [p for p in squad if p["name"] != currentplayer["name"]]
    # Initialise empty sets to store active filters
    countryfilters = set()
    positionfilters = set()
    
    def filterplayers():
        # Apply both country and position filters
        filtered = []
        for p in owned:
            if (not countryfilters or p["country"] in countryfilters) and \
               (not positionfilters or p["position"] in positionfilters):
                filtered.append(p)
        return filtered

    def showfilters():
        # Menu for toggling filters and searching for replacement players
        while True:
            clear()
            print("")
            print("FILTER OPTIONS")
            print("")
            print("Filter by Country  - C")
            print("Filter by Position - P")
            print("Search             - S")
            print("")
            print("Return             - R")
            print("")
            mysquadpageinput = input().lower()
            if mysquadpageinput == "c":
                # Show toggle menu for country filters
                togglefilter(countryfilters, sorted(set(p["country"] for p in owned)), "COUNTRY")
            elif mysquadpageinput == "p":
                # Define preferred order of positions
                preferredorder = ["GK", "LB", "CB", "RB", "CM", "LW", "RW", "ST"]
                # Limit position options to only those present in the squad
                positionspresent = [pos for pos in preferredorder if any(p["position"] == pos for p in owned)]
                togglefilter(positionfilters, positionspresent, "POSITION")
            elif mysquadpageinput == "s":
                # Show search results using the current filters
                searchresults(currentplayer, indexinxi, filterplayers(), showfilters)
                return
            elif mysquadpageinput == "r":
                # Go back to the detailed view of the current player
                viewplayerdetails(currentplayer, indexinxi)
                return

    showfilters()

def togglefilter(filterset, options, label):
    # Generic menu to toggle filters on/off for countries or positions
    while True:
        clear()
        print("")
        print(f"{label} FILTERS (toggle)")
        print("")
        # Display each option and indicate whether it is currently applied
        for i, item in enumerate(options, 1):
            tag = " (Applied)" if item in filterset else ""
            print(f"{item:<6} - {i}{tag}")
        print("")
        print(f"Return - {len(options)+1}")
        mysquadpageinput = input()
        if mysquadpageinput.isdigit():
            idx = int(mysquadpageinput)
            if 1 <= idx <= len(options):
                key = options[idx-1]
                # Toggle the selected option in the filter set
                if key in filterset:
                    filterset.remove(key)
                else:
                    filterset.add(key)
            elif idx == len(options)+1:
                # Exit the toggle menu
                break

def searchresults(currentplayer, indexinxi, filtered, returncallback):
    # Displays the list of filtered players the user can choose from to swap
    clear()
    print("")
    print("SEARCH RESULTS")
    print("")
    # Sort filtered players by rating in descending order
    sortedfiltered = sorted(filtered, key=lambda p: p["rating"], reverse=True)
    # Get names of players currently in the Starting XI (first 11)
    startingxinames = {p["name"] for p in readteamdata("squad", edit)[:11]}
    for i, p in enumerate(sortedfiltered, 1):
        # Add ' | In Starting XI' if this player is already in the starting XI
        tag = " | In Starting XI" if p["name"] in startingxinames else ""
        # Show each filtered player with their basic info
        print(f"{i}. {p['name']} - {p['country']} - {p['position']} - {p['rating']} OVR{tag}")
    print("")
    print("Return - R")
    print("")
    mysquadpageinput = input().lower()
    if mysquadpageinput == "r":
        # Return to the previous filter menu
        mysquadpage(returncallback)
    elif mysquadpageinput.isdigit():
        idx = int(mysquadpageinput)
        if 1 <= idx <= len(sortedfiltered):
            # Proceed to confirm player swap if valid index is chosen
            newplayer = sortedfiltered[idx - 1]
            confirmplayerswap(currentplayer, newplayer, indexinxi, sortedfiltered, returncallback)
        else:
            # Handle invalid numeric input
            invalid(lambda: searchresults(currentplayer, indexinxi, sortedfiltered, returncallback))

def confirmplayerswap(oldplayer, newplayer, index_in_xi, filtered, returncallback):
    # Load full player stats from ratings.json
    with open("ratings.json", "r") as f:
        ratings_data = json.load(f)
    name_to_full = {p["name"]: p for p in ratings_data}
    full_old = name_to_full.get(oldplayer["name"], oldplayer)
    full_new = name_to_full.get(newplayer["name"], newplayer)
    clear()
    print("")
    print("REPLACE")
    print("")
    print(f"Name: {full_old['name']}")
    print(f"Country: {full_old['country']}")
    print(f"Position: {full_old['position']}")
    print(f"Rating: {full_old['rating']}")
    if "stats" in full_old:
        print("Stats:")
        for stat, val in full_old["stats"].items():
            print(f"  {stat}: {val}")
    else:
        print("Stats: No stats available")
    print("")
    print("WITH")
    print("")
    print(f"Name: {full_new['name']}")
    print(f"Country: {full_new['country']}")
    print(f"Position: {full_new['position']}")
    print(f"Rating: {full_new['rating']}")
    if "stats" in full_new:
        print("Stats:")
        for stat, val in full_new["stats"].items():
            print(f"  {stat}: {val}")
    else:
        print("Stats: No stats available")
    print("")
    print("Confirm swap - Y")
    print("Cancel       - N")
    print("")
    mysquadpageinput = input().lower()
    if mysquadpageinput != "y":
        searchresults(oldplayer, index_in_xi, filtered, returncallback)
        return
    # === Perform the actual swap ===
    data = readteamdata("squad", edit)
    try:
        old_index = data.index(oldplayer)
        new_index = data.index(newplayer)
    except ValueError:
        print("Error: Player not found.")
        time.sleep(1)
        searchresults(oldplayer, index_in_xi, filtered, returncallback)
        return
    xi_count = 11
    old_in_xi = old_index < xi_count
    new_in_xi = new_index < xi_count
    # Case 1: both in XI → roles stay with positions
    if old_in_xi and new_in_xi:
        role_at_old_pos = data[old_index].get("role")
        role_at_new_pos = data[new_index].get("role")
        data[old_index], data[new_index] = newplayer, oldplayer
        if role_at_old_pos is not None:
            data[old_index]["role"] = role_at_old_pos
        else:
            data[old_index].pop("role", None)
        if role_at_new_pos is not None:
            data[new_index]["role"] = role_at_new_pos
        else:
            data[new_index].pop("role", None)
    # Case 2: one in XI, one on bench → role stays with XI position
    elif old_in_xi != new_in_xi:
        xi_index = old_index if old_in_xi else new_index
        bench_index = new_index if old_in_xi else old_index
        role_to_keep = data[xi_index].get("role")
        data[old_index], data[new_index] = newplayer, oldplayer
        if role_to_keep is not None:
            data[xi_index]["role"] = role_to_keep
        else:
            data[xi_index].pop("role", None)

        data[bench_index].pop("role", None)
    # Case 3: both on bench → just swap
    else:
        data[old_index], data[new_index] = newplayer, oldplayer
    writeteamdata(data, "squad", edit)
    clear()
    print("")
    print("Player swapped")
    print("")
    time.sleep(1)
    mysquadpage(homepage)

def tacticspage():
    clear()
    tactics = readteamdata("tactics", edit)
    directness = tactics.get("directness")
    tempo = tactics.get("tempo")
    approach = tactics.get("approach")
    dribbling = tactics.get("dribbling")
    press = tactics.get("press")
    # Show the current tactics
    print("")
    print("TACTICS")
    print("")
    print("1. Directness - " + directness)
    print("2. Tempo - " + tempo)
    print("3. Approach - " + str(approach))
    print("4. Dribbling - " + dribbling)
    print("5. Pressing intensity - " + press)
    print("")
    print("Return - R")
    print("")
    mysquadpageinput = input().upper()
    clear()
    tactics = readteamdata("tactics", edit)
    if mysquadpageinput == "1":
        print("")
        print("DIRECTNESS")
        print("")
        directoptions = [
            ("Much shorter", "1"),
            ("Shorter", "2"),
            ("Balanced", "3"),
            ("More direct", "4"),
            ("Much more direct", "5"),
        ]
        for form, num in directoptions:
            tag = " (Applied)" if form == directness else ""
            print(f"{num}. {form:<6} {tag}")
        print("")
        print("6. Return")
        print("")
        mysquadpageinput = input().strip().upper()
        if mysquadpageinput == "1":
            tactics["directness"] = "Much shorter"
        elif mysquadpageinput == "2":
            tactics["directness"] = "Shorter"
        elif mysquadpageinput == "3":
            tactics["directness"] = "Balanced"
        elif mysquadpageinput == "4":
            tactics["directness"] = "More direct"
        elif mysquadpageinput == "5":
            tactics["directness"] = "Much more direct"      
    elif mysquadpageinput == "2":
        print("")
        print("TEMPO")
        print("")
        tempooptions = [
            ("Lower", "1"),
            ("Slightly lower", "2"),
            ("Balanced", "3"),
            ("Slightly higher", "4"),
            ("Higher", "5"),
        ]
        for form, num in tempooptions:
            tag = " (Applied)" if form == tempo else ""
            print(f"{num}. {form:<6} {tag}")
        print("")
        print("6. Return")
        print("")
        mysquadpageinput = input().strip().upper()
        if mysquadpageinput == "1":
            tactics["tempo"] = "Lower"
        elif mysquadpageinput == "2":
            tactics["tempo"] = "Slightly lower"
        elif mysquadpageinput == "3":
            tactics["tempo"] = "Balanced"
        elif mysquadpageinput == "4":
            tactics["tempo"] = "Slightly higher"
        elif mysquadpageinput == "5":
            tactics["tempo"] = "Higher"
    elif mysquadpageinput == "3":
        if approach is None:
            approach = {"left": False, "middle": False, "right": False}
        def show_state():
            print("")
            print("APPROACH (toggle)")
            print("")
            print(f"1. Focus left   - {'ON' if approach['left'] else 'OFF'}")
            print(f"2. Focus middle - {'ON' if approach['middle'] else 'OFF'}")
            print(f"3. Focus right  - {'ON' if approach['right'] else 'OFF'}")
            print("")
            print("4. Return")
        print("")
        while True:
            clear()
            show_state()
            mysquadpageinput = input().strip().upper()
            if mysquadpageinput == "1":
                approach["left"] = not approach["left"]
            elif mysquadpageinput == "2":
                approach["middle"] = not approach["middle"]
            elif mysquadpageinput == "3":
                approach["right"] = not approach["right"]
            elif mysquadpageinput == "4":
                tactics["approach"] = approach
                break
    elif mysquadpageinput == "4":
        print("")
        print("DRIBBLING")
        print("")
        dribblingoptions = [
            ("Dribble less", "1"),
            ("Balanced", "2"),
            ("Run at defence", "3"),
        ]
        for form, num in dribblingoptions:
            tag = " (Applied)" if form == dribbling else ""
            print(f"{num}. {form:<4} {tag}")
        print("")
        print("4. Return")
        print("")
        mysquadpageinput = input().strip().upper()
        if mysquadpageinput == "1":
            tactics["dribbling"] = "Dribble less"
        elif mysquadpageinput == "2":
            tactics["dribbling"] = "Balanced"
        elif mysquadpageinput == "3":
            tactics["dribbling"] = "Run at defence"
    elif mysquadpageinput == "5":
        print("")
        print("PRESS")
        print("")
        pressingoptions = [
            ("Much less often", "1"),
            ("Less often", "2"),
            ("Balanced", "3"),
            ("More often", "4"),
            ("Much more often", "5"),
        ]
        for form, num in pressingoptions:
            tag = " (Applied)" if form == press else ""
            print(f"{num}. {form:<6} {tag}")
        print("")
        print("6. Return")
        print("")
        mysquadpageinput = input().strip().upper()
        if mysquadpageinput == "1":
            tactics["press"] = "Much less often"
        elif mysquadpageinput == "2":
            tactics["press"] = "Less often"
        elif mysquadpageinput == "3":
            tactics["press"] = "Balanced"
        elif mysquadpageinput == "4":
            tactics["press"] = "More often"
        elif mysquadpageinput == "5":
            tactics["press"] = "Much more often" 
    elif mysquadpageinput == "R":
        mysquadpage(currentreturncallback)
    writeteamdata(tactics, "tactics", edit)
    clear()
    tacticspage()

def mysquadpage(returncallback):
    global currentreturncallback
    if returncallback == playpage or returncallback == homepage:
        currentreturncallback = returncallback
    clear()
    print("")
    print("TEAM MANAGEMENT")
    print("")
    print(f"Team Rating:    {teamrating()} OVR")
    print(f"Team Chemistry: {teamchemistry()} / 100")
    squad = readteamdata("squad", edit)
    formation = readteamdata("formation", edit)
    player_slots, _ = formationswitch(formation)
    positions = [player_slots[i]["position"] for i in range(1, 12)]
    assigned_players = squad[:11]  # First 11 players only
    # Get actual positions directly from your squad data
    name_to_position = {p["name"]: p["position"] for p in squad}
    print("")
    # Loop over each assigned player and show whether they are in their correct position
    for i, (pos, p) in enumerate(zip(positions, assigned_players), start=1):
        actual_pos = name_to_position.get(p["name"])
        if actual_pos != pos:
            print(f"{i}. {pos:1} - {p['name']} ({p['rating']} OVR, {p['country']}) | Actual position: {actual_pos}")
        else:
            print(f"{i}. {pos:1} - {p['name']} ({p['rating']} OVR, {p['country']})")
    # If fewer than 11 players, fill the rest of the formation with [Empty]
    for pos in positions[len(assigned_players):]:
        print(f"{pos:5} - [Empty]")
    print("")
    print("Change Formation       - F")
    print("Edit Tactics           - T")
    print("View all owned players - V")
    print("Return                 - R")
    print("")
    mysquadpageinput = input().lower()
    if mysquadpageinput == "f":
        # Show formation selection menu
        current_formation = readteamdata("formation", edit)
        clear()
        print("")
        print("CHOOSE FORMATION")
        print("")
        formations = [
            ("4-4-2", "1"),
            ("4-3-3", "2"),
            ("4-5-1", "3"),
            ("4-2-2-2", "4"),
            ("5-3-2", "5"),
            ("5-2-3", "6"),
            ("5-4-1", "7")
        ]
        for form, num in formations:
            tag = " (Applied)" if form == current_formation else ""
            print(f"{form:<8} - {num}{tag}")
        print("")
        print("Return   - 8")
        print("")
        mysquadpageinput = input()
        if mysquadpageinput == "8":
            mysquadpage(currentreturncallback)
        else:
            # Update the formation based on user input
            if mysquadpageinput == "1":
                writeteamdata("4-4-2", "formation", edit)
            elif mysquadpageinput == "2":
                writeteamdata("4-3-3", "formation", edit)
            elif mysquadpageinput == "3":
                writeteamdata("4-5-1", "formation", edit)
            elif mysquadpageinput == "4":
                writeteamdata("4-2-2-2", "formation", edit)
            elif mysquadpageinput == "5":
                writeteamdata("5-3-2", "formation", edit)
            elif mysquadpageinput == "6":
                writeteamdata("5-2-3", "formation", edit)
            elif mysquadpageinput == "7":
                writeteamdata("5-4-1", "formation", edit)
            clear()
            print("")
            print("Formation changed")
            print("")
            time.sleep(1)
            mysquadpage(currentreturncallback)
    elif mysquadpageinput == "t":
        clear()
        tacticspage()
    elif mysquadpageinput == "v":
        # Show all players owned by the user, excluding those in the starting XI
        clear()
        with open("ratings.json", "r") as f:
            ratings_data = json.load(f)
        squad = readteamdata("squad", edit)
        # Starting XI = first 11 players in current squad order
        startingxi_names = {p["name"] for p in squad[:11]}
        # Players owned but not in XI
        owned_not_xi = [p for p in squad if p["name"] not in startingxi_names]
        # Map by name to full data (stats) from ratings.json
        name_to_stats = {p["name"]: p for p in ratings_data}
        displayplayers = [name_to_stats[p["name"]] for p in owned_not_xi if p["name"] in name_to_stats]
        # Sort by rating (highest first)
        displayplayers.sort(key=lambda x: x.get("rating", 0), reverse=True)
        # Show once; the viewer's Return will call mysquadpage()
        playerview(displayplayers, "ALL OWNED PLAYERS (Excluding Starting XI)", lambda: mysquadpage(returncallback), set(), set())
        return
    elif mysquadpageinput == "r":
        returncallback()
        return    
    elif mysquadpageinput.isdigit():
        idx = int(mysquadpageinput)
        if 1 <= idx <= len(assigned_players):
            selected_player = assigned_players[idx - 1]
            viewplayerdetails(selected_player, idx)        


if __name__ == "__main__":
    # Entry point for the command-line version of the game.
    # This runs only when the file is executed directly, not when imported from maingui.py
    startprogram()