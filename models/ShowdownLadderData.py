from typing import List
from .ShowdownPlayerData import ShowdownPlayerData


class ShowdownLadderData:

    def __init__(self, formatid: str, format: str, toplist: List[dict]):
        self.formatid = formatid
        self.format = format
        temp_list = []
        for player_data in toplist:
            temp_list.append(ShowdownPlayerData(**player_data))
        self.toplist = temp_list

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
