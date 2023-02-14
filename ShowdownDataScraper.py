import requests
import logging
import sys
import time
import re

from Pokemon.exceptions.NoHttpResponseException import NoHttpResponseException
from models.ShowdownLadderData import ShowdownLadderData
from models.teams import Teams
from models.users import Users
from datetime import datetime
from pymongo import MongoClient


class ShowdownDataScraper:
    format = "gen9vgc2023series2"
    ladder_base_url = "https://pokemonshowdown.com/ladder/"
    replays_base_url = "https://replay.pokemonshowdown.com/"
    database = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true")["Babiri"]
    num_teams_to_include = 100

    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", datefmt='%Y-%m-%d %H:%M:%S')

    # Ultimate goal is to construct Team and Usage MongoDB entities for a specific date and save to the database
    def scrape_showdown_for_top_teams(self):
        logging.info("Beginning data scraping.")
        #First check if data has already been scraped and saved today, and if so exit script
        self.exit_script_if_already_run_today()

        # Instantiate Team entity
        # Team entities include data from ladder url (rank, username, rating) and replays url (upload time, id for actual replay, team)
        team_entity = Teams(init_date=datetime.today(), init_format=self.format)
        logging.info(f"Current date is: {team_entity.date}")
        logging.info(f"Current format is: {team_entity.format}")

        # Get Showdown ladder data on top players
        ladder_response = self.get_ladder_data()
        top_list = ladder_response.toplist_field
        logging.info(f"Number of players returned by top ladder query: {len(top_list)}")

        # Start building DB entities for top 100 teams for TODAY and populate with ladder data
        showdown_rank_count = 1  # counter to track the player's global rank on the Showdown ladder
        website_rank_count = 1  # counter to track the rank of the team on Babiri
        # Continue to comb though top ladder until we collect 100 teams or run out of players to check
        while len(team_entity.users) < self.num_teams_to_include and showdown_rank_count <= len(top_list):
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
            replay_url = self.replays_base_url + recent_match_id
            logging.debug(f"Replay url: {replay_url}")
            team = self.get_team_list(replay_url, userid)

            user = Users(rank=showdown_rank_count, website_rank=website_rank_count, username=userid, team=team, replay_url=replay_url, rating=int(showdown_player_data.elo), upload_date=upload_date)
            logging.info(f"Team found, User object created and added to Teams list: {vars(user)}")
            team_entity.users.append(vars(user))
            showdown_rank_count += 1
            website_rank_count += 1
            time.sleep(1)
        # TODO Get usage data somehow? From Smogon i think? and add it to DB entities
        # Save entities to MongoDB tables
        logging.info(f"Number of users in Team DB entity: {len(team_entity.users)}")
        self.save_teams_to_database(team_entity)
        logging.info("Process complete.")

    def get_team_list(self, replay_url: str, userid: str):
        team = []
        replay_data = self.get_replay_data(replay_url)

        player_number = None  # either 1 or 2
        if replay_data["p1id"] == userid:
            player_number = "p1"
        else:
            player_number = "p2"
        replay_log = replay_data["log"]

        pattern = re.compile(f"poke\|{player_number}\|([\\w\\s-]+),")
        for match in pattern.finditer(replay_log):
            team.append(match.group(1).lower().replace(" ", ""))  # Format pokemon names to match sprite files
        logging.debug(f"Team list: {str(team)}")
        return team

    def save_teams_to_database(self, team_entity):
        logging.info(f"Saving teams to database.")
        mongodb_teams_collection = self.database["teams"]
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

    def get_replay_data(self, replay_url):
        try:
            replay_data = requests.get(replay_url + ".json").json()
            if replay_data is None:
                raise NoHttpResponseException("No response was received from Showdown's specific replay url.")
            return replay_data
        except:
            logging.error(f"Unexpected error when trying to get ladder data: {sys.exc_info()[0]}")
            self.get_replay_data(replay_url)

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

    def is_datetime_todays_date(self, input_datetime: datetime) -> bool:
        # Returns True if input datetime has today's Year-Month-Day
        same_year = input_datetime.year == datetime.today().year
        same_month = input_datetime.month == datetime.today().month
        same_day = input_datetime.day == datetime.today().day
        return same_year and same_month and same_day

    def exit_script_if_already_run_today(self):
        # Sorts database by descending date and grabs first record
        database_entry = self.database["teams"].find().sort("date", -1).limit(1)[0]
        # If db entries' date is today's date, exit script
        if self.is_datetime_todays_date(database_entry.get("date")):
            logging.info("Showdown data was already scrapped today, exiting script...")
            sys.exit()


def main():
    ShowdownDataScraper().scrape_showdown_for_top_teams()


if __name__ == '__main__':
    main()
