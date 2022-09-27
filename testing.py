# Website to test the API: https://docs.henrikdev.xyz/valorant.html
# Note: this is code I wrote as I fooled around with the API to figure out how it worked

import valo_api as valo
from pprint import pprint


for i in range(3):
    print(i)
    try:
        account_data = valo.get_account_details_by_name("v1", "Excalibur", "0023", True).to_dict()
        break
    except valo.exceptions.valo_api_exception.ValoAPIException as e:
        print("entered exception")
        if i != 2:
            print("Trying again", i)
            continue
        else:
            raise e
pprint(account_data)

puuid = account_data["puuid"]
for i in range(3):
    try:
        match_history = valo.get_match_history_by_puuid("v3", "na", puuid, 1, game_mode="competitive")
        break
    except valo.exceptions.valo_api_exception.ValoAPIException as e:
        if i != 2:
            print("Trying again", i)
            continue
        else:
            raise e
match_history = [match.to_dict() for match in match_history]

# pprint(match_history[0])
# all_players = match_history[0]["players"].to_dict()["all_players"]
# for player in all_players:
#     print(player.to_dict())

for match in match_history:
    rounds = [rnd.to_dict() for rnd in match["rounds"]]
    # pprint(rounds)
    round_number = 1
    for rnd in rounds:
        player_stats = [stats.to_dict() for stats in rnd["player_stats"]]
        round_kills = []
        for player_stat in player_stats:
            # pprint(player_stat)
            round_kills.extend([kill.to_dict() for kill in player_stat["kill_events"]])
        round_kills = sorted(round_kills, key=lambda x: x["kill_time_in_round"])
        print("ROUND", round_number)
        pprint(round_kills)
        round_number += 1
