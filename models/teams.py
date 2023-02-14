from typing import List
from .users import Users
from .usage import Usage
from datetime import datetime


class Teams:

    def __init__(self, init_date: datetime = None, init_format: str = None):
        self.date = init_date
        self.format = init_format
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
    def usage_field(self, value: List[Usage]):
        self.usage = value
