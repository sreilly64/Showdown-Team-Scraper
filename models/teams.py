from typing import List
from .users import Users
from .teamusage import TeamUsage
from datetime import datetime


class Teams:

    def __init__(self, date: datetime = None, format: str = None):
        self.date = date
        self.format = format
        self.users = []
        self.usage = []

    @property
    def date_field(self):
        return self.date

    @property
    def users_field(self):
        return self.users

    @property
    def format_field(self):
        return self.format

    @property
    def usage_field(self):
        return self.usage

    @date_field.setter
    def date_field(self, value: datetime):
        self.date = value

    @users_field.setter
    def users_field(self, value: List[Users]):
        self.users = value

    @format_field.setter
    def format_field(self, value: str):
        self.format = value

    @usage_field.setter
    def usage_field(self, value: List[TeamUsage]):
        self.usage = value
