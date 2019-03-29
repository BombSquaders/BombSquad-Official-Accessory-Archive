'''
I was not able to think of a different method than edit in bsSpaz method so i used this method.
'''
import bs
import bsUtils
import os
def scriptsEditor(textToFind,textToAdd):
    x = open(os.path.join("data","scripts","bsSpaz.py"),'r+').read()
    before = (x[:x.find(textToFind)])
    middle = textToAdd
    last = x[x.find(textToFind)+len(textToFind):]
    y = open(os.path.join("data","scripts","bsSpaz.py"),'w').write(before+textToFind+middle+last)
if open(os.path.join('data','scripts','bsSpaz.py'),'r+').read().find('if character == \'Wolverine\':') == -1:
    scriptsEditor('\n        self.blastRadius = 2.0','\n\n        if character == \'Wolverine\':\n			\n			def normal():\n				if not time_out:\n					self._punchPowerScale = gBasePunchPowerScale\n					self.node.handModel = bs.getModel("hand")\n				\n			def rage():\n				\n				self._punchPowerScale = 1.8\n				self.node.handModel = bs.getModel("claw")\n			def claw_extraction():\n				if self.hitPoints < 250:\n					rage()\n					bs.gameTimer(1000,bs.Call(claw_extraction))\n				elif self.hitPoints > 249:\n					normal()\n					bs.gameTimer(1000,bs.Call(claw_extraction))\n				else:\n					pass\n			def regeneration():\n				\n				if self.node.exists() and self.hitPoints < 1000 and self.hitPoints > 250:\n					bsUtils.PopupText("+10 health",color=(0,1,0),scale=1.7,position=self.node.position).autoRetain()\n					self.hitPoints += 10\n					bs.gameTimer(6000,bs.Call(regeneration))\n				else:\n					bs.gameTimer(5000,bs.Call(regeneration))\n			time_out = False\n			claw_extraction()\n			\n			regeneration()')
if open(os.path.join('data','scripts','bsSpaz.py'),'r+').read().find('if self.node.character == \"Wolverine\":') == -1:
    scriptsEditor('bsUtils.showDamageCount(\'-\' + str(int(damage/10)) + \"%\",\n                                            msg.pos, msg.forceDirection)','\n\n                elif damage > 850:\n					if self.node.character == "Wolverine":\n						time_out = True\n						def normal():\n							self._punchPowerScale = gBasePunchPowerScale\n							self.node.handModel = bs.getModel("hand")\n						def rage():\n							self._punchPowerScale = gBasePunchPowerScale + 3/20*gBasePunchPowerScale\n							self.node.handModel = bs.getModel("claw")\n							bs.gameTimer(6000,bs.Call(normal))\n						rage()')
try :
    from bsSpaz import *
except Exception:
    f1=open(os.path.join("data","scripts","bsSpaz.py"),"w+")
    f1.close()
    from bsSpaz import *

