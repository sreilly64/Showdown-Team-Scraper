import threading
import traceback
import requests
import logging
import sys
import time
import re
import os

from exceptions.HttpResponseException import HttpResponseException
from exceptions.InvalidFormatException import InvalidFormatException
from models.ShowdownPlayerData import ShowdownPlayerData
from models.ShowdownLadderData import ShowdownLadderData
from json.decoder import JSONDecodeError
from pymongo import MongoClient, InsertOne
from models.teams import Teams
from models.users import Users
from models.teamusage import TeamUsage
from models.usage import Usage
from datetime import datetime
from typing import List


class ShowdownDataScraper:
    # Configure these first 3 fields as desired
    # set 'formats' in your environment variables to a comma separated list of Pokémon Showdown format ids, example: gen9vgc2023series2, gen9doublesou, gen9doublesuu, gen9doublesubers
    formats = os.environ['formats'].replace(" ", "").split(",")
    # set 'mongoURI' and 'databaseName' in your environment variables to connect to your desired mongoDB
    database = MongoClient(os.environ['mongoURI'])[os.environ['databaseName']]
    number_teams_to_include = 10

    threads = []
    ladder_base_url = "https://pokemonshowdown.com/ladder/"
    replays_base_url = "https://replay.pokemonshowdown.com/"

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format=f"%(asctime)s | %(threadName)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # Ultimate goal is to construct Team and Usage MongoDB entities for a specific date and save to the database
    def scrape_showdown_for_top_teams(self):
        logging.info("Beginning data scraping.")
        #First check if data for the selected format has already been scraped and saved today, and if so exit script
        format = self.formats.pop()
        self.exit_script_if_already_run_today(format)

        # Get Showdown ladder data on top players
        ladder_response = self.get_ladder_data(format)
        top_list = ladder_response.toplist_field
        if len(top_list) == 0:
            raise InvalidFormatException(f"The format id {format} is invalid as the Showdown ladder api did not return any users.")
        logging.info(f"Number of players returned by {format} top ladder query: {len(top_list)}")

        # Start building database entities for top 100 teams for today and populate with ladder data
        team_entity = self.build_team_entity(top_list, format)
        logging.info(f"Number of users in {format} Team database entity: {len(team_entity.users_field)}")

        #calculate daily usage for pokemon based on user teams and add them to usage list in team_entity
        team_entity = self.calculate_usage_stats(team_entity)

        # Save entities to MongoDB tables
        self.save_teams_to_database(team_entity)
        self.save_usage_stats_to_database(team_entity)
        logging.info(f"Process completed for {format}.")

    def build_team_entity(self, top_list: List[ShowdownPlayerData], format: str) -> Teams:
        # Instantiate Team entity
        # Team entities include data from ladder url (rank, username, rating) and replays url (upload time, id for actual replay, team)
        team_entity = Teams(date=datetime.today(), format=format)
        logging.debug(f"Current date is: {team_entity.date_field}")
        logging.debug(f"Current format is: {team_entity.format_field}")

        showdown_rank_count = 1  # counter to track the player's global rank on the Showdown ladder
        website_rank_count = 1  # counter to track the rank of the team on Babiri
        # Comb through top ladder players until 100 teams are identified or list of players is exhausted
        while len(team_entity.users_field) < self.number_teams_to_include and showdown_rank_count <= len(top_list):
            #Get current player
            showdown_player_data = top_list[showdown_rank_count-1]
            logging.debug(f"Current player data: {vars(showdown_player_data)}")
            userid = showdown_player_data.userid_field

            # Use showdown ladder data objects to fetch recent replays and add that info to DB entities IF they have recent games
            recent_match_data = self.get_recent_match_data(userid, format)

            # If no recent matches, go to next user
            if len(recent_match_data) == 0:
                logging.debug(f"No recent matches were found for {userid}.")
                showdown_rank_count += 1
                continue

            # Instantiate additional fields for User object from recent_match_data
            upload_date = time.strftime('%Y-%m-%d', time.localtime(recent_match_data[0]["uploadtime"]))
            recent_match_id = recent_match_data[0]["id"]
            team = self.get_team_list(recent_match_id, userid)
            replay_url = self.replays_base_url + recent_match_id

            user = Users(rank=showdown_rank_count, website_rank=website_rank_count, username=userid, team=team, replay_url=replay_url, rating=int(showdown_player_data.elo), upload_date=upload_date)
            team_entity.users_field.append(vars(user))
            logging.info(f"{format} team found, User object created and added to Teams list: {vars(user)}")

            showdown_rank_count += 1
            website_rank_count += 1
            time.sleep(1)
        return team_entity

    #Method takes in a Teams object and calculates/adds "usage" field
    def calculate_usage_stats(self, team_entity: Teams) -> Teams:
        users = team_entity.users_field
        pokemon_count_dict = self.get_pokemon_usage_count_dict(users)  # key = Pokémon name, value = usage count
        while len(pokemon_count_dict) > 0:
            usage_count = pokemon_count_dict.popitem()
            mon = usage_count[0]
            count = usage_count[1]
            percent = round(count / self.number_teams_to_include, 2) * 100
            usage = TeamUsage(mon=mon, freq=count, percent=percent)
            team_entity.usage_field.append(vars(usage))
        return team_entity

    def get_pokemon_usage_count_dict(self, users: dict):
        pokemon_count_dict = {}  # key = Pokémon name, value = usage count
        for user in users:
            team = user["team"]
            for mon in team:
                current_count = pokemon_count_dict.get(mon, 0)
                pokemon_count_dict.update({mon: current_count + 1})
        return pokemon_count_dict

    def get_team_list(self, match_id: str, userid: str):
        team = []
        replay_data = self.get_replay_data(match_id)

        player_number = None  # either 1 or 2
        if replay_data["p1id"] == userid:
            player_number = "p1"
        else:
            player_number = "p2"
        replay_log = replay_data["log"]

        pattern = re.compile(f"poke\|{player_number}\|([\\w\\s-]+)[,|]")  # Regex for parsing Pokémon names from Showdown replay log
        for match in pattern.finditer(replay_log):
            team.append(match.group(1).lower().replace(" ", ""))  # Format Pokémon names to match file name of sprites
        logging.debug(f"Team list: {str(team)}")
        return team

    def save_teams_to_database(self, team_entity):
        logging.info(f"Saving {team_entity.format_field} teams to database...")
        mongodb_teams_collection = self.database["teams"]  # Saves to 'teams' collection in MongoDB database
        mongodb_teams_collection.insert_one(vars(team_entity))
        logging.info(f"Successfully saved {team_entity.format_field} teams to database.")

    def save_usage_stats_to_database(self, team_entity: Teams):
        logging.info(f"Saving {team_entity.format_field} usage stats to database...")
        team_usage = team_entity.usage_field  # array of usage stats for each Pokémon across teams
        date = team_entity.date_field
        format = team_entity.format_field
        usage_entity_list = []
        for usage_stat in team_usage:
            usage = {"freq": usage_stat["freq"], "percent": usage_stat["percent"]}
            mon = usage_stat["mon"]
            usage_entity = Usage(date=date, format=format, pokemon=mon, usage=usage)
            usage_entity_list.append(usage_entity)

        mongodb_teams_collection = self.database["usage"]  # Saves to 'usage' collection in MongoDB database
        mongodb_teams_collection.bulk_write([InsertOne(vars(usage_entity)) for usage_entity in usage_entity_list])

    def get_ladder_data(self, format: str) -> ShowdownLadderData:
        # Fetches a list of the top 500 players on the Pokémon Showdown ladder for the configured competitive format.
        try:
            logging.info(f"Fetching ladder for {format}.")
            ladder_response = requests.get(self.ladder_base_url + format + ".json")
            logging.debug(f"ladder_response for format {format}: {vars(ladder_response)}")
            if (ladder_response.status_code != 200) or (ladder_response is None) or (ladder_response.text == "") or (ladder_response.json() is None):
                raise HttpResponseException(f"Received bad response from ladder api for format {format}. Response: {vars(ladder_response)}")
            return ShowdownLadderData(**ladder_response.json())
        except (JSONDecodeError, HttpResponseException):
            logging.error(f"Received bad or no response from ladder api for format {format}.\nRetrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_ladder_data(format)
        except Exception:
            logging.error(f"Unexpected error occurred when trying to get ladder data for {format}. Retrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_ladder_data(format)

    def get_replay_data(self, match_id):
        # Fetches a specific replay for a given Pokémon Showdown match_id
        try:
            replay_data = requests.get(self.replays_base_url + match_id + ".json")
            logging.debug(f"replay_data for match_id {match_id}: {vars(replay_data)}")
            if (replay_data.status_code != 200) or (replay_data is None) or (replay_data.text == "") or (replay_data.json() is None):
                raise HttpResponseException(f"Received bad response from replay api for id {match_id}. Response: {vars(replay_data)}")
            return replay_data.json()
        except (JSONDecodeError, HttpResponseException):
            logging.error(f"Received bad or no response from replay api for id {match_id}. Retrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_replay_data(match_id)
        except Exception:
            logging.error(f"Unexpected error occurred when trying to get replay for id {match_id}. Retrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_replay_data(match_id)

    def get_recent_match_data(self, userid: str, format: str):
        # Fetches all recent Pokémon Showdown match replays (of only the configured format) for a given user
        try:
            recent_matches = requests.get(self.replays_base_url + "search.json?user=" + userid + "&format=" + format)
            logging.debug(f"recent_matches for user {userid} and format {format}: {vars(recent_matches)}")
            if (recent_matches.status_code != 200) or (recent_matches is None) or (recent_matches.text == "") or (recent_matches.json() is None):
                raise HttpResponseException(f"Received bad response from recent matches api for {userid} and {format}. Response: {vars(recent_matches)}")
            logging.debug(f"Number of recent matches: {len(recent_matches.json())}")
            return recent_matches.json()
        except (JSONDecodeError, HttpResponseException):
            logging.error(f"Received bad or no response from recent matches api for user {userid} and format {format}. Retrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_recent_match_data(userid, format)
        except Exception:
            logging.error(f"Unexpected error occurred when trying to get recent matches for user {userid} and format {format}. Retrying...")
            traceback.print_exc()
            time.sleep(3)
            return self.get_recent_match_data(userid, format)

    def exit_script_if_already_run_today(self, format: str):
        # Check if database is empty for the given format to avoid IndexError
        if self.database["teams"].count_documents({"format": f"{format}"}) == 0:
            logging.debug(f"No database entries found for format {format}.")
            return
        # Find records with matching format and sort results by descending date to select the most recent record
        latest_database_entry = self.database["teams"].find({"format": f"{format}"}).sort("date", -1).limit(1)[0]
        # If the database entry date is today's date, exit script
        database_entry_date = datetime.strftime(latest_database_entry.get("date"), '%Y-%m-%d')
        todays_date = datetime.today().strftime('%Y-%m-%d')
        if database_entry_date == todays_date:
            logging.info(f"Showdown data for {format} was already scrapped today, closing thread...")
            sys.exit()

    def main(self):
        number_of_threads = len(self.formats)
        if number_of_threads == 0 or (number_of_threads == 1 and self.formats[0] == ""):
            raise InvalidFormatException("No Pokemon Showdown formats were provided.")
        for _ in range(number_of_threads):
            t = threading.Thread(target=self.scrape_showdown_for_top_teams)
            t.daemon = True
            self.threads.append(t)

        for i in range(number_of_threads):
            logging.info(f"Starting thread {i+1}.")
            self.threads[i].start()

        for i in range(number_of_threads):
            self.threads[i].join()


if __name__ == '__main__':
    ShowdownDataScraper().main()
