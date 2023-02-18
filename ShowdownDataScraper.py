import requests
import logging
import sys
import time
import re
import os

from exceptions.NoHttpResponseException import NoHttpResponseException
from models.ShowdownPlayerData import ShowdownPlayerData
from models.ShowdownLadderData import ShowdownLadderData
from models.teams import Teams
from models.users import Users
from datetime import datetime
from pymongo import MongoClient
from typing import List


class ShowdownDataScraper:
    # Configure these first 3 fields as desired
    format = os.environ['format']  # set 'format' in your environment variables to desired Pokemon Showdown format id, example: gen9vgc2023series2
    database = MongoClient(os.environ['mongoURI'])[os.environ['databaseName']]  # set 'mongoURI' and 'databaseName' in your environment variables to connect to your desired mongoDB
    number_teams_to_include = 100

    ladder_base_url = "https://pokemonshowdown.com/ladder/"
    replays_base_url = "https://replay.pokemonshowdown.com/"

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # Ultimate goal is to construct Team and Usage MongoDB entities for a specific date and save to the database
    def scrape_showdown_for_top_teams(self):
        logging.info("Beginning data scraping.")
        #First check if data for the selected format has already been scraped and saved today, and if so exit script
        self.exit_script_if_already_run_today()

        # Get Showdown ladder data on top players
        ladder_response = self.get_ladder_data()
        top_list = ladder_response.toplist_field
        logging.info(f"Number of players returned by top ladder query: {len(top_list)}")

        # Start building DB entities for top 100 teams for TODAY and populate with ladder data
        team_entity = self.build_team_entity(top_list)
        # TODO Get usage data somehow? From Smogon i think? and add it to DB entities
        # Save entities to MongoDB tables
        logging.info(f"Number of users in Team DB entity: {len(team_entity.users_field)}")
        self.save_teams_to_database(team_entity)
        logging.info("Process complete.")

    def build_team_entity(self, top_list: List[ShowdownPlayerData]) -> Teams:
        # Instantiate Team entity
        # Team entities include data from ladder url (rank, username, rating) and replays url (upload time, id for actual replay, team)
        team_entity = Teams(date=datetime.today(), format=self.format)
        logging.info(f"Current date is: {team_entity.date_field}")
        logging.info(f"Current format is: {team_entity.format_field}")

        showdown_rank_count = 1  # counter to track the player's global rank on the Showdown ladder
        website_rank_count = 1  # counter to track the rank of the team on Babiri
        # Comb through top ladder players until 100 teams are identified or list of players is exhausted
        while len(team_entity.users_field) < self.number_teams_to_include and showdown_rank_count <= len(top_list):
            #Get current player
            showdown_player_data = top_list[showdown_rank_count-1]
            logging.debug(f"Current player data: {vars(showdown_player_data)}")
            userid = showdown_player_data.userid_field

            # Use showdown ladder data objects to fetch recent replays and add that info to DB entities IF they have recent games
            recent_match_data = self.get_recent_match_data(userid)
            logging.debug(f"Number of recent matches: {len(recent_match_data)}")
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
            logging.info(f"Team found, User object created and added to Teams list: {vars(user)}")

            showdown_rank_count += 1
            website_rank_count += 1
            time.sleep(1)
        return team_entity

    def get_team_list(self, match_id: str, userid: str):
        team = []
        replay_data = self.get_replay_data(match_id)

        player_number = None  # either 1 or 2
        if replay_data["p1id"] == userid:
            player_number = "p1"
        else:
            player_number = "p2"
        replay_log = replay_data["log"]

        pattern = re.compile(f"poke\|{player_number}\|([\\w\\s-]+),")  # Regex for parsing Pokemon names from Showdown replay log
        for match in pattern.finditer(replay_log):
            team.append(match.group(1).lower().replace(" ", ""))  # Format pokemon names to match file name of sprites
        logging.debug(f"Team list: {str(team)}")
        return team

    def save_teams_to_database(self, team_entity):
        logging.info(f"Saving teams to database.")
        mongodb_teams_collection = self.database["teams"]  # Saves to 'teams' collection in MongoDB database
        mongodb_teams_collection.insert_one(vars(team_entity))

    def get_ladder_data(self) -> ShowdownLadderData:
        # Fetches a list of the top 500 players on the Pokemon Showdown ladder for the configured competitive format.
        try:
            logging.info(f"Fetching ladder for {self.format}.")
            ladder_response = requests.get(self.ladder_base_url + self.format + ".json").json()
            if ladder_response is None:
                raise NoHttpResponseException("No response was received from Showdown's ladder url.")
            return ShowdownLadderData(**ladder_response)
        except:
            logging.error(f"Unexpected error when trying to get ladder data: {sys.exc_info()[0]}")
            self.get_ladder_data()

    def get_replay_data(self, match_id):
        # Fetches a specific replay for a given Pokemon Showdown match_id
        try:
            replay_data = requests.get(self.replays_base_url + match_id + ".json").json()
            if replay_data is None:
                raise NoHttpResponseException("No response was received from Showdown's specific replay url.")
            return replay_data
        except:
            logging.error(f"Unexpected error when trying to get ladder data: {sys.exc_info()[0]}")
            self.get_replay_data(match_id)

    def get_recent_match_data(self, userid):
        # Fetches all recent Pokemon Showdown match replays (of only the configured format) for a given user
        try:
            recent_matches = requests.get(self.replays_base_url + "search.json?user=" + userid + "&format=" + self.format).json()
            if recent_matches is None:
                raise NoHttpResponseException("No response was received from Showdown's recent replays url.")
            return recent_matches
        except:
            logging.error(f"Unexpected error when trying to get ladder data: {sys.exc_info()[0]}")
            self.get_recent_match_data(userid)

    def exit_script_if_already_run_today(self):
        # Check if database is empty for the given format to avoid IndexError
        if self.database["teams"].count_documents({"format": f"{self.format}"}) == 0:
            logging.debug(f"No database entries found for format {self.format}.")
            return
        # Find records with matching format and sort results by descending date to select the most recent record
        latest_database_entry = self.database["teams"].find({"format": f"{self.format}"}).sort("date", -1).limit(1)[0]
        # If the database entry date is today's date, exit script
        database_entry_date = datetime.strftime(latest_database_entry.get("date"), '%Y-%m-%d')
        todays_date = datetime.today().strftime('%Y-%m-%d')
        if database_entry_date == todays_date:
            logging.info("Showdown data was already scrapped today, exiting script...")
            sys.exit()


def main():
    ShowdownDataScraper().scrape_showdown_for_top_teams()


if __name__ == '__main__':
    main()
