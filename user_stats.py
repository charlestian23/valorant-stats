import valo_api as valo
from pprint import pprint


def get_round_kills_in_chronological_order(rnd: dict()) -> list[dict()]:
    player_stats = [stats.to_dict() for stats in rnd["player_stats"]]
    round_kills = []
    for player_stat in player_stats:
        round_kills.extend([kill.to_dict() for kill in player_stat["kill_events"]])
    return sorted(round_kills, key=lambda x: x["kill_time_in_round"])


class UserStats:
    def __init__(self, name: str, tag: str, attempts: int = 3):
        self.name = name
        self.tag = tag
        for i in range(attempts):
            try:
                self.account_data = valo.get_account_details_by_name("v1", self.name, self.tag, True).to_dict()
                break
            except valo.exceptions.valo_api_exception.ValoAPIException as e:
                if i != 2 and e.status != 404 and e.status != 429:
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

    # TODO: Modify method to account for the possibility that player is resurrected by a teammate Sage (note that at the
    #  time of this writing, the API is missing data and so it is not possible to account for Sage's resurrection)
    def get_kast(self, match: dict(), trade_window: int=5000) -> float:
        kast_rounds = 0
        rounds = [rnd.to_dict() for rnd in match["rounds"]]
        for rnd in rounds:
            round_kills = get_round_kills_in_chronological_order(rnd)

            kat = False
            died_without_trade = False
            check_if_traded = False
            killer_puuid = None
            time_of_death = -1
            for kill in round_kills:
                if check_if_traded:
                    # Player died without getting traded
                    # Note: It is possible to still get a kill after dying (e.g. Brimstone or Viper post-plant molly),
                    #  which is why the code does not break after verifying that the player died without getting traded
                    if kill["kill_time_in_round"] - time_of_death > trade_window:
                        check_if_traded = False
                        killer_puuid = None
                        time_of_death = -1

                    # Player died but got traded
                    elif kill["victim_puuid"] == killer_puuid:
                        kast_rounds += 1
                        kat = True
                        died_without_trade = False
                        break

                # Player got a kill
                if kill["killer_puuid"] == self.puuid:
                    kast_rounds += 1
                    kat = True
                    break

                # Player got an assist
                if self.has_assist(kill["assistants"]):
                    kast_rounds += 1
                    kat = True
                    break

                # Player died during the round
                if kill["victim_puuid"] == self.puuid:
                    check_if_traded = True
                    time_of_death = kill["kill_time_in_round"]
                    died_without_trade = True

            # Player survived the round
            if not kat and not died_without_trade:
                kast_rounds += 1

        return kast_rounds / len(rounds) * 100

    def has_assist(self, assistants: list[valo.responses.match_history.MatchRoundAssistantV3]) -> bool:
        for assistant in assistants:
            if assistant.to_dict()["assistant_puuid"] == self.puuid:
                return True
        return False


if __name__ == "__main__":
    name = str(input("Enter your Valorant name: "))
    tag = str(input("Enter your Valorant tag: "))
    me = UserStats(name, tag)
    pprint(me.get_statistics_for_last_ten_matches())
