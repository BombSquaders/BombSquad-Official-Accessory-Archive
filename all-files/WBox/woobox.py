from bsSpaz import *

##############################WBox#########################
t = Appearance("WBox")
t.colorTexture = "wbTex"
t.colorMaskTexture = "wbTex2"
t.defaultColor = (0.5,0.5,0.5)
t.defaultHighlight = (0,1,1)
t.iconTexture = "wbTex3"
t.iconMaskTexture = "wbTex2"
t.headModel =     "wbHead"
t.torsoModel =    "wbTorso"
t.pelvisModel =   "wbPelvis"
t.upperArmModel = "wbUpperArm"
t.foreArmModel =  "wbForeArm"
t.handModel =     "wbHand"
t.upperLegModel = "wbUpperLeg"
t.lowerLegModel = "wbLowerLeg"
t.toesModel =     "wbToes"
wbSounds =    ['wb1','wb2','wb3','wb4']
wbHitSounds = ['wbHit1','wbHit2']
t.attackSounds = wbSounds
t.jumpSounds = wbSounds
t.impactSounds = wbHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = wbSounds
t.fallSounds=["bearFall"]
t.style = 'agent'