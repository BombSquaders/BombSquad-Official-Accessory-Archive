import bs
import bsUtils
import bsSpaz
from bsSpaz import *
import copy

default_spaz_init = copy.deepcopy(bsSpaz.Spaz.__init__)


def __init__(self, color=(1, 1, 1), highlight=(0.5, 0.5, 0.5),
             character="Spaz", sourcePlayer=None, startInvincible=True,
             canAcceptPowerups=True, powerupsExpire=False, demoMode=False):
    default_spaz_init(self, color, highlight, character, sourcePlayer, startInvincible, canAcceptPowerups,
                 powerupsExpire, demoMode)

    if character == 'Wolverine':

        def normal():
            self._punchPowerScale = gBasePunchPowerScale
            self.node.handModel = bs.getModel("wvhand")

        def rage():

            self._punchPowerScale = 1.8
            self.node.handModel = bs.getModel("wvclaw")

        def claw_state():
            try:
                if self.hitPoints < 250:
                    rage()
                    bs.gameTimer(1000, bs.Call(claw_state))
                elif self.hitPoints > 249:
                    normal()
                    bs.gameTimer(1000, bs.Call(claw_state))
            except:
                pass

        def regeneration():

            try:
                if self.node.exists() and self.hitPoints < self.hitPointsMax and self.hitPoints > 249:
                    bsUtils.PopupText("+10", color=(0, 1, 0), scale=1.7,
                                      position=self.node.position).autoRetain()
                    self.hitPoints += 10
                    bs.gameTimer(4000, bs.Call(regeneration))
                else:
                    bs.gameTimer(3500, bs.Call(regeneration))
            except:
                pass

        claw_state()
        regeneration()


##############################Wolverine#########################
t = Appearance("Wolverine")
t.colorTexture = "wvtex"
t.colorMaskTexture = "wvtex2"
t.defaultColor = (0.5, 0.5, 0.5)
t.defaultHighlight = (0, 1, 1)
t.iconTexture = "wvtex3"
t.iconMaskTexture = "wvtex3"
t.headModel = "wvhead"
t.torsoModel = "wvtorso"
t.pelvisModel = "wvpelvis"
t.upperArmModel = "wvupperArm"
t.foreArmModel = "wvforeArm"
t.handModel = "wvhand"
t.upperLegModel = "wvupperLeg"
t.lowerLegModel = "wvlowerLeg"
t.toesModel = "wvtoes"
t.attackSounds = ['wv1', 'wv2', 'wv3', 'wv4']
t.jumpSounds = ['wv1', 'wv2', 'wv3', 'wv4']
t.impactSounds = ['wvhit']
t.deathSounds = ["bearDeath"]
t.pickupSounds = ['wv1', 'wv2', 'wv3', 'wv4']
t.fallSounds = ["bearFall"]
t.style = 'agent'

bsSpaz.Spaz.__init__ = __init__
bs.Spaz.__init__ = __init__
