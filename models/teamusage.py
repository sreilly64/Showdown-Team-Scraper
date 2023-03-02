class TeamUsage:
    def __init__(self, mon: str = None, freq: int = None, percent: float = None):
        self.mon = mon
        self.freq = freq
        self.percent = percent

    @property
    def mon_field(self):
        return self.mon

    @property
    def freq_field(self):
        return self.freq

    @property
    def percent_field(self):
        return self.percent

    @mon_field.setter
    def mon_field(self, value: str):
        self.mon = value

    @freq_field.setter
    def freq_field(self, value: int):
        self.freq = value

    @percent_field.setter
    def percent_field(self, value: float):
        self.percent = value
