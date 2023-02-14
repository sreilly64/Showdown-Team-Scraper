from typing import List


class Users:
    def __init__(self, rank: int = None, website_rank: int = None, username: str = None, team: List[str] = [],
                 replay_url: str = None, rating: int = None, upload_date: str = None):
        self.rank = rank
        self.website_rank = website_rank
        self.username = username
        self.team = team
        self.replay_url = replay_url
        self.rating = rating
        self.upload_date = upload_date

    @property
    def rank_field(self):
        return self.rank

    @property
    def website_rank_field(self):
        return self.website_rank

    @property
    def username_field(self):
        return self.username

    @property
    def team_field(self):
        return self.team

    @property
    def replay_url_field(self):
        return self.replay_url

    @property
    def rating_field(self):
        return self.rating

    @property
    def upload_date_field(self):
        return self.upload_date

    @rank_field.setter
    def rank_field(self, value: int):
        self.rank = value

    @website_rank_field.setter
    def website_rank_field(self, value: int):
        self.website_rank = value

    @username_field.setter
    def username_field(self, value: str):
        self.username = value

    @team_field.setter
    def team_field(self, value: List[str]):
        self.team = value

    @replay_url_field.setter
    def replay_url_field(self, value: str):
        self.replay_url = value

    @rating_field.setter
    def rating_field(self, value: int):
        self.rating = value

    @upload_date_field.setter
    def upload_date_field(self, value: str):
        self.upload_date = value
