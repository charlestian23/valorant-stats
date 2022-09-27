# https://docs.henrikdev.xyz/valorant.html
import valo_api as valo
from pprint import pprint

for i in range(3):
    try:
        account_data = valo.get_account_details_by_name("v1", "Excalibur", "0023", True).to_dict()
    except valo.exceptions.valo_api_exception.ValoAPIException as e:
        if i != 2:
            print("Trying again")
            continue
        else:
            raise e
pprint(account_data)

puuid = account_data["puuid"]
for i in range(3):
    try:
        match_history = valo.get_match_history_by_puuid("v3", "na", puuid, 10, game_mode="competitive")
    except valo.exceptions.valo_api_exception.ValoAPIException as e:
        if i != 2:
            print("Trying again")
            continue
        else:
            raise e
match_history = [match.to_dict() for match in match_history]
pprint(match_history)
