from bsSpaz import *

##############################Wolverine#########################
t = Appearance("Wolverine")
t.colorTexture = "tex"
t.colorMaskTexture = "tex2"
t.defaultColor = (0.5,0.5,0.5)
t.defaultHighlight = (0,1,1)
t.iconTexture = "tex3"
t.iconMaskTexture = "tex3"
t.headModel =     "head"
t.torsoModel =    "torso"
t.pelvisModel =   "pelvis"
t.upperArmModel = "upperArm"
t.foreArmModel =  "foreArm"
t.handModel =     "hand"
t.upperLegModel = "upperLeg"
t.lowerLegModel = "lowerLeg"
t.toesModel =     "toes"
bearSounds =    ['bear1','bear2','bear3','bear4']
bearHitSounds = ['bearHit1','bearHit2']
t.attackSounds = bearSounds
t.jumpSounds = bearSounds
t.impactSounds = bearHitSounds
t.deathSounds=["bearDeath"]
t.pickupSounds = bearSounds
t.fallSounds=["bearFall"]
t.style = 'agent'