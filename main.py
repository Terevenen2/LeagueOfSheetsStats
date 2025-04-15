from rich.console import Console
import requests
import datetime
import pyperclip

# Replace with your actual Riot API key
API_KEY = ""
HEADERS = {"X-Riot-Token": API_KEY}
console = Console()

def replace_last(source, target, replacement):
    # rpartition returns a tuple: (head, separator, tail)
    head, sep, tail = source.rpartition(target)
    # If the target is found, 'sep' will be non-empty.
    if sep:
        return head + replacement + tail
    return source  # target not found, return original string


def get_puuid(gameName: str, tagLine: str) -> str:
    """
    Retrieve puuid using the Riot Account API.
    """
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Error fetching account data: {response.text}")
    data = response.json()
    return data["puuid"]


def get_match_ids(puuid: str, count: int = 20) -> list:
    """
    Get the most recent ranked match ids for a given puuid.
    """
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"type": "ranked", "start": 0, "count": count}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching match ids: {response.text}")
    return response.json()


def get_match_details(match_id: str) -> dict:
    """
    Retrieve details for a given match ID.
    """
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Error fetching match details for {match_id}: {response.text}")
    return response.json()


def process_match(match_json: dict, puuid: str) -> dict:
    """
    Process a single match's JSON to extract and calculate the desired fields.
    """
    info = match_json["info"]

    # Convert game creation from ms epoch to date (jj/mm/yyyy)
    gameCreation = info["gameCreation"]
    game_date = datetime.datetime.fromtimestamp(gameCreation / 1000).strftime("%d/%m/%Y")

    # Game duration in seconds
    game_duration = info.get("gameDuration", 0)
    game_duration_min = game_duration / 60 if game_duration > 0 else 1  # avoid division by zero

    # Find our participant's details using puuid
    participant_data = None
    for participant in info["participants"]:
        if participant["puuid"] == puuid:
            participant_data = participant
            break
    if not participant_data:
        raise Exception("Participant data not found in match details.")

    champion = participant_data["championName"]
    mode = info.get("gameMode", "N/A")
    win = participant_data["win"]
    result = "Win" if win else "Loss"
    kills = participant_data["kills"]
    deaths = participant_data["deaths"]
    assists = participant_data["assists"]
    kda = (kills + assists) / deaths if deaths != 0 else (kills + assists)

    # Calculate total team kills from the same team
    team_id = participant_data["teamId"]
    team_kills = sum(p["kills"] for p in info["participants"] if p["teamId"] == team_id)

    # Kill participation percentage (if team kills > 0)
    kill_participation = ((kills + assists) / team_kills * 100) if team_kills > 0 else 0

    # Other in-game statistics
    wards = participant_data.get("wardsPlaced", 0)
    pink = participant_data.get("pinksPurchased", 0)
    vision_score = participant_data.get("visionScore", 0)
    vision_score_per_min = vision_score / game_duration_min

    # Farm: total minions killed (lane + jungle)
    total_minions = participant_data.get("totalMinionsKilled", 0)
    neutral_minions = participant_data.get("neutralMinionsKilled", 0)
    farm = total_minions + neutral_minions
    cs_per_min = farm / game_duration_min

    gold = participant_data.get("goldEarned", 0)
    gold_per_min = gold / game_duration_min

    # Prepare the row of results in a dictionary
    match_result = {
        "DATE": game_date,#DATE
        "champion": champion,
        "mode": mode,
        "result": result.upper().replace('LOSS', 'LOSE'),
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "KDA": '=(F:F+H:H)/IF(G:G=0;1;G:G)',
        "kill_totaux": team_kills,
        "kill_particip": '=IF(J:J=0;0;(F:F+H:H)/J:J)',
        "game_duration_sec": round(game_duration/60, 2),
        "wards": wards,
        "pink": pink,
        "vision_score": vision_score,
        "vision_score_per_min": '=O:O/L:L',
        "farm": farm,
        "cs_per_min": '=Q:Q/L:L',
        "gold": gold,
        "gold_per_min": '=S:S/L:L'
    }
    return match_result


def main():
    # Prompt the user for gameName and tagLine

    try:
        # Get puuid based on provided gameName and tagLine
        username = input("Enter your league of legends username :")
        tag = input("Enter your tag :")
        console.print(
            "Get your Riot Games API key here: [link=https://developer.riotgames.com/]Riot Games Developer Portal[/link]", style="green")
        API_KEY = input("Enter your Riot Games API key :")
        global HEADERS
        HEADERS = {"X-Riot-Token": API_KEY}
        puuid = get_puuid(username, tag)
        console.print(f"Retrieved puuid: {puuid}")

        nb_games_to_get = input("Number of games you want to retrieve :")

        # Retrieve recent match IDs
        match_ids = get_match_ids(puuid, int(nb_games_to_get))
        console.print(f"Found {len(match_ids)} matches.")

        # Process each match to build a list of match data dictionaries
        results = ''
        for match_id in match_ids:
            console.print(f"Processing match: {match_id}")
            match_json = get_match_details(match_id)
            match_data = process_match(match_json, puuid)
            row = ''
            for elem in match_data.values():
                row += str(elem) + '\t'
            results += replace_last(row, '\t', '\n')

        # Convert the results to JSON-formatted string
        results = results.replace(".", ",")
        # Copy the JSON to clipboard
        pyperclip.copy(results)
        console.print("Match data copied to clipboard successfully!", style="green")
        #console.print(results)

    except Exception as e:
        console.print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
