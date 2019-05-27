from bsMap import *
import bs
import random
import bsVector
import bsUtils
import bsSpaz
from bsSpaz import *


class HockeyStadiumFlying(Map):
    import hockeyStadiumDefs as defs
    name = "3D Fly Hockey Stadium"
    playTypes = ['melee', 'hockey', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'hockeyStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['models'] = (bs.getModel('hockeyStadiumOuter'),
                          bs.getModel('hockeyStadiumInner'),
                          bs.getModel('hockeyStadiumStands'))
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel('hockeyStadiumCollide')
        data['tex'] = bs.getTexture('hockeyStadium')
        data['standsTex'] = bs.getTexture('footballStadium')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision', 'friction', 0.01))
        data['iceMaterial'] = m
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode("terrain", delegate=self, attrs={
            'model': self.preloadData['models'][0],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['iceMaterial']]})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillModel'],
            'vrOnly': True,
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['standsTex']})
        self.floor = bs.newNode("terrain", attrs={
            "model": self.preloadData['models'][1],
            "colorTexture": self.preloadData['tex'],
            "opacity": 0.92,
            "opacityInLowOrMediumQuality": 1.0,
            "materials": [bs.getSharedObject('footingMaterial'),
                          self.preloadData['iceMaterial']]})
        self.stands = bs.newNode("terrain", attrs={
            "model": self.preloadData['models'][2],
            "visibleInReflections": False,
            "colorTexture": self.preloadData['standsTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.floorReflection = True
        bsGlobals.debrisFriction = 0.3
        bsGlobals.debrisKillHeight = -0.3
        bsGlobals.tint = (1.2, 1.3, 1.33)
        bsGlobals.ambientColor = (1.15, 1.25, 1.6)
        bsGlobals.vignetteOuter = (0.66, 0.67, 0.73)
        bsGlobals.vignetteInner = (0.93, 0.93, 0.95)
        bsGlobals.vrCameraOffset = (0, -0.8, -1.1)
        bsGlobals.vrNearClip = 0.5
        self.isHockey = True


registerMap(HockeyStadiumFlying)


class FootballStadiumFlying(Map):
    import footballStadiumDefs as defs
    name = "3D Fly Football Stadium"
    playTypes = ['melee', 'football', 'teamFlag', 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'footballStadiumPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel("footballStadium")
        data['vrFillModel'] = bs.getModel('footballStadiumVRFill')
        data['collideModel'] = bs.getCollideModel("footballStadiumCollide")
        data['tex'] = bs.getTexture("footballStadium")
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['model'],
            'collideModel': self.preloadData['collideModel'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        bs.newNode('terrain',
                   attrs={'model': self.preloadData['vrFillModel'],
                          'lighting': False,
                          'vrOnly': True,
                          'background': True,
                          'colorTexture': self.preloadData['tex']})
        g = bs.getSharedObject('globals')
        g.tint = (1.3, 1.2, 1.0)
        g.ambientColor = (1.3, 1.2, 1.0)
        g.vignetteOuter = (0.57, 0.57, 0.57)
        g.vignetteInner = (0.9, 0.9, 0.9)
        g.vrCameraOffset = (0, -0.8, -1.1)
        g.vrNearClip = 0.5

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0]) / boxScale[0]
        z = (p.z() - boxPosition[2]) / boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)


registerMap(FootballStadiumFlying)


class BridgitMapFlying(Map):
    import bridgitLevelDefs as defs
    name = "3D Fly Bridgit"
    playTypes = ["melee", "teamFlag", 'keepAway']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bridgitPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel("bridgitLevelTop")
        data['modelBottom'] = bs.getModel("bridgitLevelBottom")
        data['modelBG'] = bs.getModel("natureBackground")
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel("bridgitLevelCollide")
        data['tex'] = bs.getTexture("bridgitLevelColor")
        data['modelBGTex'] = bs.getTexture("natureBackgroundColor")
        data['collideBG'] = bs.getCollideModel("natureBackgroundCollide")
        data['railingCollideModel'] = \
            bs.getCollideModel("bridgitLevelRailingCollide")
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['modelTop'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['bgVRFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['bgMaterial'],
                          bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.3)
        bsGlobals.ambientColor = (1.1, 1.2, 1.3)
        bsGlobals.vignetteOuter = (0.65, 0.6, 0.55)
        bsGlobals.vignetteInner = (0.9, 0.9, 0.93)


registerMap(BridgitMapFlying)


class BigGMapFlying(Map):
    import bigGDefs as defs
    name = '3D Fly Big G'
    playTypes = ['race', 'melee', 'keepAway', 'teamFlag',
                 'kingOfTheHill', 'conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'bigGPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['modelTop'] = bs.getModel('bigG')
        data['modelBottom'] = bs.getModel('bigGBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('bigGCollide')
        data['tex'] = bs.getTexture('bigG')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['bumperCollideModel'] = bs.getCollideModel('bigGBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'color': (0.7, 0.7, 0.7),
            'model': self.preloadData['modelTop'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBottom'],
            'color': (0.7, 0.7, 0.7),
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['bgVRFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['bumperCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['bgMaterial'],
                          bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.3)
        bsGlobals.ambientColor = (1.1, 1.2, 1.3)
        bsGlobals.vignetteOuter = (0.65, 0.6, 0.55)
        bsGlobals.vignetteInner = (0.9, 0.9, 0.93)


registerMap(BigGMapFlying)


class RoundaboutMapFlying(Map):
    import roundaboutLevelDefs as defs
    name = '3D Fly Roundabout'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'roundaboutPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('roundaboutLevel')
        data['modelBottom'] = bs.getModel('roundaboutLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('roundaboutLevelCollide')
        data['tex'] = bs.getTexture('roundaboutLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = \
            bs.getCollideModel('roundaboutLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0, -1, 1))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['bgVRFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['bgMaterial'],
                          bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0, 1.05, 1.1)
        bsGlobals.ambientColor = (1.0, 1.05, 1.1)
        bsGlobals.shadowOrtho = True
        bsGlobals.vignetteOuter = (0.63, 0.65, 0.7)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)


registerMap(RoundaboutMapFlying)


class MonkeyFaceMapFlying(Map):
    import monkeyFaceLevelDefs as defs
    name = '3D Fly Monkey Face'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'monkeyFacePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('monkeyFaceLevel')
        data['bottomModel'] = bs.getModel('monkeyFaceLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('monkeyFaceLevelCollide')
        data['tex'] = bs.getTexture('monkeyFaceLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = \
            bs.getCollideModel('monkeyFaceLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['bottomModel'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['bgVRFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['bgMaterial'],
                          bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.2, 1.2)
        bsGlobals.ambientColor = (1.2, 1.3, 1.3)
        bsGlobals.vignetteOuter = (0.60, 0.62, 0.66)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)
        bsGlobals.vrCameraOffset = (-1.4, 0, 0)


registerMap(MonkeyFaceMapFlying)


class ZigZagMapFlying(Map):
    import zigZagLevelDefs as defs
    name = '3D Fly Zigzag'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'zigzagPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('zigZagLevel')
        data['modelBottom'] = bs.getModel('zigZagLevelBottom')
        data['modelBG'] = bs.getModel('natureBackground')
        data['bgVRFillModel'] = bs.getModel('natureBackgroundVRFill')
        data['collideModel'] = bs.getCollideModel('zigZagLevelCollide')
        data['tex'] = bs.getTexture('zigZagLevelColor')
        data['modelBGTex'] = bs.getTexture('natureBackgroundColor')
        data['collideBG'] = bs.getCollideModel('natureBackgroundCollide')
        data['railingCollideModel'] = bs.getCollideModel('zigZagLevelBumper')
        data['bgMaterial'] = bs.Material()
        data['bgMaterial'].addActions(actions=('modifyPartCollision',
                                               'friction', 10.0))
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBG'],
            'lighting': False,
            'colorTexture': self.preloadData['modelBGTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['bgVRFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['modelBGTex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['bgMaterial'],
                          bs.getSharedObject('deathMaterial')]})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.0, 1.15, 1.15)
        bsGlobals.ambientColor = (1.0, 1.15, 1.15)
        bsGlobals.vignetteOuter = (0.57, 0.59, 0.63)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)
        bsGlobals.vrCameraOffset = (-1.5, 0, 0)


registerMap(ZigZagMapFlying)


class ThePadMapFlying(Map):
    import thePadLevelDefs as defs
    name = '3D Fly The Pad'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'thePadPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('thePadLevel')
        data['bottomModel'] = bs.getModel('thePadLevelBottom')
        data['collideModel'] = bs.getCollideModel('thePadLevelCollide')
        data['tex'] = bs.getTexture('thePadLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections for efficiency
        data['bgModel'] = bs.getModel('thePadBG')
        data['railingCollideModel'] = bs.getCollideModel('thePadLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('thePadVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['bottomModel'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillMoundModel'],
            'lighting': False,
            'vrOnly': True,
            'color': (0.56, 0.55, 0.47),
            'background': True,
            'colorTexture': self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.1, 1.1, 1.0)
        bsGlobals.ambientColor = (1.1, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.65, 0.75)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)


registerMap(ThePadMapFlying)


class DoomShroomMapFlying(Map):
    import doomShroomLevelDefs as defs
    name = '3D Fly Doom Shroom'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'doomShroomPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('doomShroomLevel')
        data['collideModel'] = bs.getCollideModel('doomShroomLevelCollide')
        data['tex'] = bs.getTexture('doomShroomLevelColor')
        data['bgTex'] = bs.getTexture('doomShroomBGColor')
        data['bgModel'] = bs.getModel('doomShroomBG')
        data['vrFillModel'] = bs.getModel('doomShroomVRFill')
        data['stemModel'] = bs.getModel('doomShroomStem')
        data['collideBG'] = bs.getCollideModel('doomShroomStemCollide')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.foo = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.stem = bs.newNode('terrain', attrs={
            'model': self.preloadData['stemModel'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.bgCollide = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['collideBG'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          bs.getSharedObject('deathMaterial')]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.82, 1.10, 1.15)
        bsGlobals.ambientColor = (0.9, 1.3, 1.1)
        bsGlobals.shadowOrtho = False
        bsGlobals.vignetteOuter = (0.76, 0.76, 0.76)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.99)

    def _isPointNearEdge(self, p, running=False):
        x = p.x()
        z = p.z()
        xAdj = x * 0.125
        zAdj = (z + 3.7) * 0.2
        if running:
            xAdj *= 1.4
            zAdj *= 1.4
        return (xAdj * xAdj + zAdj * zAdj > 1.0)


registerMap(DoomShroomMapFlying)


class LakeFrigidMapFlying(Map):
    import lakeFrigidDefs as defs
    name = '3D Fly Lake Frigid'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'race']

    @classmethod
    def getPreviewTextureName(cls):
        return 'lakeFrigidPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('lakeFrigid')
        data['modelTop'] = bs.getModel('lakeFrigidTop')
        data['modelReflections'] = bs.getModel('lakeFrigidReflections')
        data['collideModel'] = bs.getCollideModel('lakeFrigidCollide')
        data['tex'] = bs.getTexture('lakeFrigid')
        data['texReflections'] = bs.getTexture('lakeFrigidReflections')
        data['vrFillModel'] = bs.getModel('lakeFrigidVRFill')
        m = bs.Material()
        m.addActions(actions=('modifyPartCollision', 'friction', 0.01))
        data['iceMaterial'] = m
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial'),
                          self.preloadData['iceMaterial']]})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['modelTop'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['modelReflections'],
            'lighting': False,
            'overlay': True,
            'opacity': 0.15,
            'colorTexture': self.preloadData['texReflections']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['tex']})
        g = bs.getSharedObject('globals')
        g.tint = (1, 1, 1)
        g.ambientColor = (1, 1, 1)
        g.shadowOrtho = True
        g.vignetteOuter = (0.86, 0.86, 0.86)
        g.vignetteInner = (0.95, 0.95, 0.99)
        g.vrNearClip = 0.5
        self.isHockey = True


registerMap(LakeFrigidMapFlying)


class TipTopMapFlying(Map):
    import tipTopLevelDefs as defs
    name = '3D Fly Tip Top'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'kingOfTheHill']

    @classmethod
    def getPreviewTextureName(cls):
        return 'tipTopPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('tipTopLevel')
        data['bottomModel'] = bs.getModel('tipTopLevelBottom')
        data['collideModel'] = bs.getCollideModel('tipTopLevelCollide')
        data['tex'] = bs.getTexture('tipTopLevelColor')
        data['bgTex'] = bs.getTexture('tipTopBGColor')
        data['bgModel'] = bs.getModel('tipTopBG')
        data['railingCollideModel'] = bs.getCollideModel('tipTopLevelBumper')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0, -0.2, 2.5))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'color': (0.7, 0.7, 0.7),
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['bottomModel'],
            'lighting': False,
            'color': (0.7, 0.7, 0.7),
            'colorTexture': self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'color': (0.4, 0.4, 0.4),
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (0.8, 0.9, 1.3)
        bsGlobals.ambientColor = (0.8, 0.9, 1.3)
        bsGlobals.vignetteOuter = (0.79, 0.79, 0.69)
        bsGlobals.vignetteInner = (0.97, 0.97, 0.99)


registerMap(TipTopMapFlying)


class CragCastleMapFlying(Map):
    import cragCastleDefs as defs
    name = '3D Fly Crag Castle'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'cragCastlePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('cragCastleLevel')
        data['bottomModel'] = bs.getModel('cragCastleLevelBottom')
        data['collideModel'] = bs.getCollideModel('cragCastleLevelCollide')
        data['tex'] = bs.getTexture('cragCastleLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections
        data['bgModel'] = bs.getModel('thePadBG')
        data['railingCollideModel'] = \
            bs.getCollideModel('cragCastleLevelBumper')
        data['vrFillMoundModel'] = bs.getModel('cragCastleVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['bottomModel'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillMoundModel'],
            'lighting': False,
            'vrOnly': True,
            'color': (0.2, 0.25, 0.2),
            'background': True,
            'colorTexture': self.preloadData['vrFillMoundTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.shadowOrtho = True
        bsGlobals.shadowOffset = (0, 0, -5.0)
        bsGlobals.tint = (1.15, 1.05, 0.75)
        bsGlobals.ambientColor = (1.15, 1.05, 0.75)
        bsGlobals.vignetteOuter = (0.6, 0.65, 0.6)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.95)
        bsGlobals.vrNearClip = 1.0


registerMap(CragCastleMapFlying)


class TowerDMapFlying(Map):
    import towerDLevelDefs as defs
    name = '3D Fly Tower D'
    playTypes = ['melee']

    @classmethod
    def getPreviewTextureName(cls):
        return 'towerDPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('towerDLevel')
        data['modelBottom'] = bs.getModel('towerDLevelBottom')
        data['collideModel'] = bs.getCollideModel('towerDLevelCollide')
        data['tex'] = bs.getTexture('towerDLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr sections
        data['bgModel'] = bs.getModel('thePadBG')
        data['playerWallCollideModel'] = bs.getCollideModel('towerDPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision',
                                                        'friction', 0.0)))
        # anything that needs to hit the wall can apply this material
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial', data['collideWithWallMaterial']),
            actions=(('modifyPartCollision', 'collide', False)))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0, 1, 1))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillMoundModel'],
            'lighting': False,
            'vrOnly': True,
            'color': (0.53, 0.57, 0.5),
            'background': True,
            'colorTexture': self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.playerWall = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['playerWallCollideModel'],
            'affectBGDynamics': False,
            'materials': [self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.15, 1.11, 1.03)
        bsGlobals.ambientColor = (1.2, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.73, 0.7)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.95)

    def _isPointNearEdge(self, p, running=False):
        # see if we're within edgeBox
        boxes = self.defs.boxes
        boxPosition = boxes['edgeBox'][0:3]
        boxScale = boxes['edgeBox'][6:9]
        boxPosition2 = boxes['edgeBox2'][0:3]
        boxScale2 = boxes['edgeBox2'][6:9]
        x = (p.x() - boxPosition[0]) / boxScale[0]
        z = (p.z() - boxPosition[2]) / boxScale[2]
        x2 = (p.x() - boxPosition2[0]) / boxScale2[0]
        z2 = (p.z() - boxPosition2[2]) / boxScale2[2]
        # if we're outside of *both* boxes we're near the edge
        return ((x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)
                and (x2 < -0.5 or x2 > 0.5 or z2 < -0.5 or z2 > 0.5))


registerMap(TowerDMapFlying)


class StepRightUpMapFlying(Map):
    import stepRightUpLevelDefs as defs
    name = '3D Fly Step Right Up'
    playTypes = ['melee', 'keepAway', 'teamFlag', 'conquest']

    @classmethod
    def getPreviewTextureName(cls):
        return 'stepRightUpPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('stepRightUpLevel')
        data['modelBottom'] = bs.getModel('stepRightUpLevelBottom')
        data['collideModel'] = bs.getCollideModel('stepRightUpLevelCollide')
        data['tex'] = bs.getTexture('stepRightUpLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme should chop this into vr/non-vr chunks
        data['bgModel'] = bs.getModel('thePadBG')
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0, -1, 2))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.nodeBottom = bs.newNode('terrain', delegate=self, attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillMoundModel'],
            'lighting': False,
            'vrOnly': True,
            'color': (0.53, 0.57, 0.5),
            'background': True,
            'colorTexture': self.preloadData['vrFillMoundTex']})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.1, 1.0)
        bsGlobals.ambientColor = (1.2, 1.1, 1.0)
        bsGlobals.vignetteOuter = (0.7, 0.65, 0.75)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)


registerMap(StepRightUpMapFlying)


class CourtyardMapFlying(Map):
    import courtyardLevelDefs as defs
    name = '3D Fly Courtyard'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'courtyardPreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('courtyardLevel')
        data['modelBottom'] = bs.getModel('courtyardLevelBottom')
        data['collideModel'] = bs.getCollideModel('courtyardLevelCollide')
        data['tex'] = bs.getTexture('courtyardLevelColor')
        data['bgTex'] = bs.getTexture('menuBG')
        # fixme - chop this into vr and non-vr chunks
        data['bgModel'] = bs.getModel('thePadBG')
        data['playerWallCollideModel'] = \
            bs.getCollideModel('courtyardPlayerWall')
        data['playerWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(actions=(('modifyPartCollision',
                                                        'friction', 0.0)))
        # anything that needs to hit the wall should apply this.
        data['collideWithWallMaterial'] = bs.Material()
        data['playerWallMaterial'].addActions(
            conditions=('theyDontHaveMaterial',
                        data['collideWithWallMaterial']),
            actions=('modifyPartCollision', 'collide', False))
        data['vrFillMoundModel'] = bs.getModel('stepRightUpVRFillMound')
        data['vrFillMoundTex'] = bs.getTexture('vrFillMound')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self)
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['modelBottom'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillMoundModel'],
            'lighting': False,
            'vrOnly': True,
            'color': (0.53, 0.57, 0.5),
            'background': True,
            'colorTexture': self.preloadData['vrFillMoundTex']})
        # in co-op mode games, put up a wall to prevent players
        # from getting in the turrets (that would foil our brilliant AI)
        if isinstance(bs.getSession(), bs.CoopSession):
            self.playerWall = bs.newNode('terrain', attrs={
                'collideModel': self.preloadData['playerWallCollideModel'],
                'affectBGDynamics': False,
                'materials': [self.preloadData['playerWallMaterial']]})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.17, 1.1)
        bsGlobals.ambientColor = (1.2, 1.17, 1.1)
        bsGlobals.vignetteOuter = (0.6, 0.6, 0.64)
        bsGlobals.vignetteInner = (0.95, 0.95, 0.93)

    def _isPointNearEdge(self, p, running=False):
        # count anything off our ground level as safe (for our platforms)
        # see if we're within edgeBox
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0]) / boxScale[0]
        z = (p.z() - boxPosition[2]) / boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)


registerMap(CourtyardMapFlying)


class RampageMapFlying(Map):
    import rampageLevelDefs as defs
    name = '3D Fly Rampage'
    playTypes = ['melee', 'keepAway', 'teamFlag']

    @classmethod
    def getPreviewTextureName(cls):
        return 'rampagePreview'

    @classmethod
    def onPreload(cls):
        data = {}
        data['model'] = bs.getModel('rampageLevel')
        data['bottomModel'] = bs.getModel('rampageLevelBottom')
        data['collideModel'] = bs.getCollideModel('rampageLevelCollide')
        data['tex'] = bs.getTexture('rampageLevelColor')
        data['bgTex'] = bs.getTexture('rampageBGColor')
        data['bgTex2'] = bs.getTexture('rampageBGColor2')
        data['bgModel'] = bs.getModel('rampageBG')
        data['bgModel2'] = bs.getModel('rampageBG2')
        data['vrFillModel'] = bs.getModel('rampageVRFill')
        data['railingCollideModel'] = bs.getCollideModel('rampageBumper')
        return data

    def fly(self):
        return True

    def __init__(self):
        Map.__init__(self, vrOverlayCenterOffset=(0, 0, 2))
        self.node = bs.newNode('terrain', delegate=self, attrs={
            'collideModel': self.preloadData['collideModel'],
            'model': self.preloadData['model'],
            'colorTexture': self.preloadData['tex'],
            'materials': [bs.getSharedObject('footingMaterial')]})
        self.bg = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex']})
        self.bottom = bs.newNode('terrain', attrs={
            'model': self.preloadData['bottomModel'],
            'lighting': False,
            'colorTexture': self.preloadData['tex']})
        self.bg2 = bs.newNode('terrain', attrs={
            'model': self.preloadData['bgModel2'],
            'lighting': False,
            'background': True,
            'colorTexture': self.preloadData['bgTex2']})
        bs.newNode('terrain', attrs={
            'model': self.preloadData['vrFillModel'],
            'lighting': False,
            'vrOnly': True,
            'background': True,
            'colorTexture': self.preloadData['bgTex2']})
        self.railing = bs.newNode('terrain', attrs={
            'collideModel': self.preloadData['railingCollideModel'],
            'materials': [bs.getSharedObject('railingMaterial')],
            'bumper': True})
        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.tint = (1.2, 1.1, 0.97)
        bsGlobals.ambientColor = (1.3, 1.2, 1.03)
        bsGlobals.vignetteOuter = (0.62, 0.64, 0.69)
        bsGlobals.vignetteInner = (0.97, 0.95, 0.93)

    def _isPointNearEdge(self, p, running=False):
        boxPosition = self.defs.boxes['edgeBox'][0:3]
        boxScale = self.defs.boxes['edgeBox'][6:9]
        x = (p.x() - boxPosition[0]) / boxScale[0]
        z = (p.z() - boxPosition[2]) / boxScale[2]
        return (x < -0.5 or x > 0.5 or z < -0.5 or z > 0.5)


registerMap(RampageMapFlying)


def onJumpPress2(self):
    """
    Called to 'press jump' on this spaz;
    used by player or AI connections.
    """
    if not self.node.exists(): return
    t = bs.getGameTime()
    try:
        if bs.getActivity().getMap().fly() == True:
            if not self.node.isAlive(): return
            self.node.handleMessage(
                "impulse", self.node.position[0], self.node.position[1], self.node.position[2],
                self.node.moveLeftRight * 10, self.node.position[1] + 35, self.node.moveUpDown * -10,
                5, 5, 0, 0,
                self.node.moveLeftRight * 10, self.node.position[1] + 35, self.node.moveUpDown * -10)
        else:
            if t - self.lastJumpTime >= self._jumpCooldown:
                self.node.jumpPressed = True
                self.lastJumpTime = t
            self._turboFilterAddPress('jump')
    except AttributeError:
        if t - self.lastJumpTime >= self._jumpCooldown:
            self.node.jumpPressed = True
            self.lastJumpTime = t
        self._turboFilterAddPress('jump')
    except Exception:
        if t - self.lastJumpTime >= self._jumpCooldown:
            self.node.jumpPressed = True
            self.lastJumpTime = t
        self._turboFilterAddPress('jump')
        bs.printException()


bsSpaz.Spaz.onJumpPress = onJumpPress2
