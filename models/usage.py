from datetime import datetime


class Usage:
    def __init__(self, date: datetime = None, format: str = None, pokemon: str = None, usage: dict = {}):
        self.date = date
        self.format = format
        self.pokemon = pokemon
        self.usage = usage

    @property
    def date_field(self):
        return self.date

    @property
    def format_field(self):
        return self.format

    @property
    def pokemon_field(self):
        return self.pokemon

    @property
    def usage_field(self):
        return self.usage

    @date_field.setter
    def date_field(self, value: datetime):
        self.date = value

    @format_field.setter
    def format_field(self, value: str):
        self.format = value

    @pokemon_field.setter
    def pokemon_field(self, value: str):
        self.pokemon = value

    @usage_field.setter
    def usage_field(self, value: dict):
        self.usage = value
