from typing import List
from .ShowdownPlayerData import ShowdownPlayerData


class ShowdownLadderData:

    def __init__(self, formatid: str = None, format: str = None, toplist: List[ShowdownPlayerData] = None):
        self.formatid = formatid
        self.format = format
        self.toplist = toplist

    @property
    def formatid_field(self):
        return self.formatid

    @property
    def format_field(self):
        return self.format

    @property
    def toplist_field(self):
        return self.toplist

    @formatid_field.setter
    def formatid_field(self, value: str):
        self.formatid = value

    @format_field.setter
    def format_field(self, value: str):
        self.format = value

    @toplist_field.setter
    def toplist_field(self, value: List[ShowdownPlayerData]):
        self.toplist = value