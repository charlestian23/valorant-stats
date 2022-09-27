import valo_api as valo
from pprint import pprint


class UserStats:
    def __init__(self, name: str, tag: str, attempts: int = 3):
        self.name = name
        self.tag = tag
        for i in range(attempts):
            try:
                self.account_data = valo.get_account_details_by_name("v1", self.name, self.tag, True).to_dict()
                break
            except valo.exceptions.valo_api_exception.ValoAPIException as e:
                if i != 2:
                    print("Failed to get account details, trying again...")
                    continue
                else:
                    raise e
        self.puuid = self.account_data["puuid"]
        for i in range(attempts):
            try:
                match_history = valo.get_match_history_by_puuid("v3", "na", self.puuid, 10, game_mode="competitive")
                break
            except valo.exceptions.valo_api_exception.ValoAPIException as e:
                if i != 2:
                    print("Failed to get match history... trying again")
                    continue
                else:
                    raise e
        self.match_history = [match.to_dict() for match in match_history]

    def get_statistics_for_last_ten_matches(self) -> list[dict]:
        statistics = []
        for match in self.match_history:
            statistics.append(self.get_match_statistics(match))
        return statistics

    def get_match_statistics(self, match: dict) -> dict:
        statistics = dict()

        statistics["map"] = match["metadata"].to_dict()["map"]

        team = None
        all_players = match["players"].to_dict()["all_players"]
        for player in all_players:
            player_data = player.to_dict()
            if player_data["puuid"] == self.puuid:
                team = player_data["team"].lower()
                statistics["agent"] = player_data["character"]
                break
        score_stats = match["teams"].to_dict()[team].to_dict()
        statistics["score"] = [score_stats["rounds_won"], score_stats["rounds_lost"], score_stats["has_won"]]

        statistics["kda"] = self.get_kda(match)
        statistics["hs%"] = self.get_hs_percent(match)
        statistics["kast"] = self.get_kast(match)
        return statistics

    def get_kda(self, match: dict()) -> (int, int, int):
        kill_count = 0
        death_count = 0
        assist_count = 0
        kills = [kill.to_dict() for kill in match["kills"]]
        for kill in kills:
            if kill["killer_puuid"] == self.puuid:
                kill_count += 1
            if kill["victim_puuid"] == self.puuid:
                death_count += 1
            for assistant in kill["assistants"]:
                if assistant.to_dict()["assistant_puuid"] == self.puuid:
                    assist_count += 1
                    break
        return kill_count, death_count, assist_count

    def get_hs_percent(self, match: dict()) -> float:
        total_shots = 0
        total_headshots = 0
        rounds = [rnd.to_dict() for rnd in match["rounds"]]
        for rnd in rounds:
            for temp in rnd["player_stats"]:
                stats = temp.to_dict()
                if stats["player_puuid"] == self.puuid:
                    total_headshots += stats["headshots"]
                    total_shots += stats["headshots"] + stats["bodyshots"] + stats["legshots"]
        return total_headshots / total_shots * 100



    # TODO: implement method
    def get_kast(self, match: dict()) -> float:
        return None


if __name__ == "__main__":
    me = UserStats("Excalibur", "0023")
    pprint(me.get_statistics_for_last_ten_matches())
