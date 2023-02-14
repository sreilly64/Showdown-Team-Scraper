class ShowdownPlayerData:
    def __init__(self, userid: str = None, username: str = None, w: int = None, l: int = None, t: int = None,
                 gxe: float = None, r: float = None, rd: float = None, sigma: int = None, rptime: str = None,
                 rpr: float = None, rprd: float = None, rpsigma: int = None, elo: float = None):
        self.userid = userid
        self.username = username
        self.w = w
        self.l = l
        self.t = t
        self.gxe = gxe
        self.r = r
        self.rd = rd
        self.sigma = sigma
        self.rptime = rptime
        self.rpr = rpr
        self.rprd = rprd
        self.rpsigma = rpsigma
        self.elo = elo

    @property
    def userid_field(self):
        return self.userid

    @property
    def username_field(self):
        return self.username

    @property
    def w_field(self):
        return self.w

    @property
    def l_field(self):
        return self.l

    @property
    def t_field(self):
        return self.t

    @property
    def gxe_field(self):
        return self.gxe

    @property
    def r_field(self):
        return self.r

    @property
    def rd_field(self):
        return self.rd

    @property
    def sigma_field(self):
        return self.sigma

    @property
    def rptime_field(self):
        return self.rptime

    @property
    def rpr_field(self):
        return self.rpr

    @property
    def rprd_field(self):
        return self.rprd

    @property
    def rpsigma_field(self):
        return self.rpsigma

    @property
    def elo_field(self):
        return self.elo

    @userid_field.setter
    def userid_field(self, value: str):
        self.userid = value

    @username_field.setter
    def username_field(self, value: str):
        self.username = value

    @w_field.setter
    def w_field(self, value: int):
        self.w = value

    @l_field.setter
    def l_field(self, value: int):
        self.l = value

    @t_field.setter
    def t_field(self, value: int):
        self.t = value

    @gxe_field.setter
    def gxe_field(self, value: float):
        self.gxe = value

    @r_field.setter
    def r_field(self, value: float):
        self.r = value

    @rd_field.setter
    def rd_field(self, value: float):
        self.rd = value

    @sigma_field.setter
    def sigma_field(self, value: int):
        self.sigma = value

    @rptime_field.setter
    def rptime_field(self, value: str):
        self.rptime = value

    @rpr_field.setter
    def rpr_field(self, value: float):
        self.rpr = value

    @rprd_field.setter
    def rprd_field(self, value: float):
        self.rprd = value

    @rpsigma_field.setter
    def rpsigma_field(self, value: int):
        self.rpsigma = value

    @elo_field.setter
    def elo_field(self, value: float):
        self.elo = value
