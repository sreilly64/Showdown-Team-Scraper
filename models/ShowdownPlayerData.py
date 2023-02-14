class ShowdownPlayerData(object):
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
