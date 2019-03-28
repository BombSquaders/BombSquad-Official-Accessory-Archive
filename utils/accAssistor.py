import bsMainMenu
from bsMainMenu import *
import bsUI
from bsUI import *
import accManager

DEBUG = False


class Widget(bs.Widget):
    _instance = None
    _values = dict(upWidget=None, downWidget=None, leftWidget=None, rightWidget=None,
                   showBufferTop=None, showBufferBottom=None, showBufferLeft=None,
                   showBufferRight=None, autoSelect=None)
    _required = []
    _func = bs.widget
    _can_create = False
    _values_funcs = {}

    def __init__(self, **kwargs):
        if not self._can_create:
            raise Exception("cant create widget of type " + str(self.__class__))
        for key in self._required:
            if key not in kwargs:
                raise ValueError("expected " + key)
        self._instance = self._call_func(self._func, kwargs)
        self._values_funcs = {}
        self._values = {}
        for cls in [self.__class__] + list(self.__class__.__bases__):
            self._values_funcs[cls._func] = cls._values
            self._values.update(cls._values)
        self._values.update(kwargs)

    def _call_func(self, func, kwargs):
        d = {}
        for key, value in kwargs.items():
            d[key] = value
            if isinstance(value, Widget):
                d[key] = value._instance
        if DEBUG:
            print("bs.{}(**{})".format(func.__name__, d))
        return func(**d)

    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def reset_value(self, key):
        setattr(self, key, self.__class__._values[key])

    def activate(self, *args, **kwargs):
        return self._instance.activate(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._instance.delete(*args, **kwargs)

    def exists(self, *args, **kwargs):
        return self._instance.exists(*args, **kwargs)

    def getChildren(self, *args, **kwargs):
        return self._instance.getChildren(*args, **kwargs)

    def getScreenSpaceCenter(self, *args, **kwargs):
        return self._instance.getScreenSpaceCenter(*args, **kwargs)

    def getSelectedChild(self, *args, **kwargs):
        return self._instance.getSelectedChild(*args, **kwargs)

    def getWidgetType(self, *args, **kwargs):
        return self._instance.getWidgetType(*args, **kwargs)

    def __getattr__(self, key):
        if hasattr(self._instance, key):
            return getattr(self._instance, key)
        if key in self._values:
            return self._values[key]
        raise AttributeError("type object '{}' has no attribute '{}'".format(type(self), key))

    def __setattr__(self, key, value):
        if DEBUG:
            print("__setattr__({}, {})".format(repr(key), value))
        for func, values in self._values_funcs.items():
            if key in values:
                self._call_func(func, {"edit": self._instance, key: value})
                self._values[key] = value
                return
        self.__dict__[key] = value

    def __repr__(self):
        return object.__repr__(self)

    def __str__(self):
        return object.__str__(self)


class TextWidget(Widget):
    _values = dict(parent=None, size=None, position=None, vAlign=None, hAlign=None, editable=False,
                   padding=None, onReturnPressCall=None, selectable=None, onActivateCall=None,
                   query=None, maxChars=None, color=None, clickActivate=None, scale=None,
                   alwaysHighlight=None, drawController=None, description=None, transitionDelay=None,
                   flatness=None, enabled=None, forceInternalEditing=False, alwaysShowCarat=None,
                   maxWidth=None, maxHeight=None, big=False)  # FIXME: check default values
    _required = ["parent"]
    _func = bs.textWidget
    _can_create = True

    # FIXME: textWidget.set(text=...) shadows instance method
    def text(self):
        return self._func(query=self._instance)


class ButtonWidget(Widget):
    _values = dict(parent=None, size=None, position=None, onActivateCall=None, label=None,
                   color=None, texture=None, textScale=None, enableSound=True, modelTransparent=None,
                   modelOpaque=None, transitionDelay=None, onSelectCall=None, extraTouchBorderScale=None,
                   buttonType=None, touchOnly=None, showBufferTop=None, icon=None, iconScale=None,
                   iconTint=None, iconColor=None, autoSelect=None, repeat=None, maskTexture=None,
                   tintTexture=None, tintColor=None)  # FIXME: check default values
    _required = ["parent", "position", "size"]
    _func = bs.buttonWidget
    _can_create = True
    COLOR_GREY = (0.52, 0.48, 0.63)
    TEXTCOLOR_GREY = (0.65, 0.6, 0.7)


class CheckBoxWidget(Widget):
    _values = dict(parent=None, size=None, position=None, value=None, clickSelect=None,
                   onActivateCall=None, onValueChangeCall=None, onSelectCall=None,
                   isRadioButton=False, scale=None, maxWidth=None, autoSelect=None,
                   color=None)  # FIXME: check default values
    _required = ["parent", "position"]
    _func = bs.checkBoxWidget
    _can_create = True

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        if not self.onValueChangeCall:
            def f(val):
                print(val)
                self._values["value"] = val

            self._func(edit=self._instance, onValueChangeCall=f)

    def _call_func(self, func, kwargs):
        d = {}
        for key, value in kwargs.items():
            d[key] = value
            if isinstance(value, Widget):
                d[key] = value._instance
            if key == "onValueChangeCall":
                def w(value):
                    def f(val):
                        self._values["value"] = val
                        value(val)

                    return f

                d[key] = w(value)
        return func(**d)


class ContainerWidget(Widget):
    _values = dict(parent=None, size=None, position=None, selectedChild=None, transition=None,
                   cancelButton=None, startButton=None, rootSelectable=None, onActivateCall=None,
                   claimsLeftRight=None, claimsTab=None, selectionLoops=None, selectionLoopToParent=None,
                   scale=None, type=None, onOutsideClickCall=None, singleDepth=None, visibleChild=None,
                   stackOffset=None, color=None, onCancelCall=None, printListExitInstructions=None,
                   clickActivate=None, alwaysHighlight=None, selectable=None,
                   scaleOriginStackOffset=None)  # FIXME: check default values
    _required = ["size"]
    _func = bs.containerWidget
    _can_create = True

    def doTransition(self, transition):
        self.set(transition=transition)


class ScrollWidget(Widget):
    _values = dict(parent=None, size=None, position=None, captureArrows=False, onSelectCall=None,
                   centerSmallContent=None, color=None, highlight=None,
                   borderOpacity=None)  # FIXME: check default values
    _required = ["parent", "position", "size"]
    _func = bs.scrollWidget
    _can_create = True


class ColumnWidget(Widget):
    _values = dict(parent=None, size=None, position=None, singleDepth=None,
                   printListExitInstructions=None, leftBorder=None,
                   selectedChild=None, visibleChild=None)  # FIXME: check default values
    _required = ["parent"]
    _func = bs.columnWidget
    _can_create = True


class HScrollWidget(Widget):
    _values = dict(parent=None, size=None, position=None, captureArrows=False, onSelectCall=None,
                   centerSmallContent=None, color=None, highlight=None,
                   borderOpacity=None)  # FIXME: check default values
    _required = ["parent", "position", "size"]
    _func = bs.hScrollWidget
    _can_create = True


class ImageWidget(Widget):
    _values = dict(parent=None, size=None, position=None, color=None, texture=None,
                   model=None, modelTransparent=None, modelOpaque=None, hasAlphaChannel=True,
                   tintTexture=None, tintColor=None, transitionDelay=None, drawController=None,
                   tiltScale=None, maskTexture=None)  # FIXME: check default values
    _required = ["parent", "size", "position"]
    _func = bs.imageWidget
    _can_create = True


class RowWidget(Widget):
    _values = dict(parent=None, size=None, position=None, selectable=False)
    _required = ["parent", "size", "position"]
    _func = bs.rowWidget
    _can_create = True


class NewMainMenuActivity(MainMenuActivity):
    def onTransitionIn(self):
        import bsInternal
        bs.Activity.onTransitionIn(self)
        global gDidInitialTransition
        random.seed(123)
        self._logoNode = None
        self._customLogoTexName = None
        self._wordActors = []
        env = bs.getEnvironment()

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa) -
        # any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = bs.getEnvironment()['vrMode']

        if not bs.getEnvironment().get('toolbarTest', True):
            self.myName = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'bottom',
                'hAlign': 'center',
                'color': (1.0, 1.0, 1.0, 1.0) if vrMode else (0.5, 0.6, 0.5, 0.6),
                'flatness': 1.0,
                'shadow': 1.0 if vrMode else 0.5,
                'scale': (0.9 if (env['interfaceType'] == 'small' or vrMode)
                          else 0.7),  # FIXME need a node attr for this
                'position': (0, 10),
                'vrDepth': -10,
                'text': u'\xa9 2018 Eric Froemling'}))

        # throw up some text that only clients can see so they know that the
        # host is navigating menus while they're just staring at an
        # empty-ish screen..
        self._hostIsNavigatingText = bs.NodeActor(bs.newNode('text', attrs={
            'text': bs.Lstr(resource='hostIsNavigatingMenusText',
                            subs=[('${HOST}',
                                   bsInternal._getAccountDisplayString())]),
            'clientOnly': True,
            'position': (0, -200),
            'flatness': 1.0,
            'hAlign': 'center'}))
        if not gDidInitialTransition and hasattr(self, 'myName'):
            bs.animate(self.myName.node, 'opacity', {2300: 0, 3000: 1.0})

        # TEMP - testing hindi text
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'left',
                'color': (1, 1, 1, 1),
                'shadow': 1.0,
                'flatness': 0.0,
                'scale': 1,
                'position': (-500, -40),
                'text': ('\xe0\xa4\x9c\xe0\xa4\xbf\xe0\xa4\xb8 \xe0\xa4\xad'
                         '\xe0\xa5\x80 \xe0\xa4\x9a\xe0\xa5\x80\xe0\xa5\x9b '
                         '\xe0\xa4\x95\xe0\xa5\x8b \xe0\xa4\x9b\xe0\xa5\x81'
                         '\xe0\xa4\x8f\xe0\xa4\x81\xe0\xa4\x97\xe0\xa5\x87 '
                         '\xe0\xa4\x89\xe0\xa4\xb8\xe0\xa4\xb8\xe0\xa5\x87 '
                         '\xe0\xa4\x9a\xe0\xa4\xbf\xe0\xa4\xaa\xe0\xa4\x95'
                         '\n\xe0\xa4\x9c\xe0\xa4\xbe\xe0\xa4\xaf\xe0\xa5\x87'
                         '\xe0\xa4\x82\xe0\xa4\x97\xe0\xa5\x87 .. \xe0\xa4'
                         '\x87\xe0\xa4\xb8\xe0\xa4\x95\xe0\xa4\xbe \xe0\xa4'
                         '\xae\xe0\xa5\x9b\xe0\xa4\xbe \xe0\xa4\xb2\xe0\xa5'
                         '\x87\xe0\xa4\x82 !')}))
        # TEMP - test emoji
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'left',
                'color': (1, 1, 1, 1),
                'shadow': 1.0,
                'flatness': 1.0,
                'scale': 1,
                'position': (-500, -40),
                'text': ('TST: "deivit \xf0\x9f\x90\xa2"')}))
        # TEMP - testing something; forgot what
        if False:
            # bs.screenMessage("TESTING: "+'TST: "deivit \xf0\x9f\x90\xa2"')
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'left',
                'color': (1, 1, 1, 1),
                'shadow': 1.0,
                'flatness': 0.0,
                'scale': 1,
                'position': (-500, 0),
                'text': u('        \u3147\u3147                             '
                          '            \uad8c\ucc2c\uadfc                   '
                          '                        \uae40\uc6d0\uc7ac\n     '
                          '   \ub10c                                        '
                          '    \uc804\uac10\ud638\nlll\u0935\u093f\u0936\u0947'
                          '\u0937 \u0927\u0928\u094d\u092f\u0935\u093e'
                          '\u0926:\n')}))
        # TEMP - test chinese text
        if False:
            self.tTest = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'center',
                'color': (1, 1, 1, 1),
                'shadow': 1.0,
                'flatness': 0.0,
                'scale': 1,
                'position': (-400, -40),
                'text': ('TST: "\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b\xb4\xe5\xa4'
                         '\x9a\xe5\x9b\xbe\xe6\xa0\x87"\n\xe6\x88\x90\xe5'
                         '\xb0\xb1\xe4\xb8\xad|         foo\n\xe8\xb4\xa6'
                         '\xe6\x88\xb7 \xe7\x99\xbb\xe9\x99\x86foo\nend"'
                         '\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b\xb4\xe5\xa4\x9a'
                         '\xe5\x9b\xbe\xe6\xa0\x87"\nend"\xe8\x8e\xb7\xe5'
                         '\x8f\x96\xe6\x9b\xb4\xe5\xa4\x9a\xe5\x9b\xbe\xe6'
                         '\xa0\x87"\nend2"\xe8\x8e\xb7\xe5\x8f\x96\xe6\x9b'
                         '\xb4\xe5\xa4\x9a\xe5\x9b\xbe\xe6\xa0\x87"\n')}))

        # FIXME - shouldn't be doing things conditionally based on whether
        # the host is vr mode or not (clients may not be or vice versa)
        # - any differences need to happen at the engine level
        # so everyone sees things in their own optimal way
        vrMode = env['vrMode']
        interfaceType = env['interfaceType']

        # in cases where we're doing lots of dev work lets
        # always show the build number
        forceShowBuildNumber = False

        if not bs.getEnvironment().get('toolbarTest', True):
            if env['debugBuild'] or env['testBuild'] or forceShowBuildNumber:
                if env['debugBuild']:
                    text = bs.Lstr(value='${V} (${B}) (${D})',
                                   subs=[('${V}', env['version']),
                                         ('${B}', str(env['buildNumber'])),
                                         ('${D}', bs.Lstr(resource='debugText')
                                          )])
                else:
                    text = bs.Lstr(value='${V} (${B})',
                                   subs=[('${V}', env['version']),
                                         ('${B}', str(env['buildNumber']))])
            else:
                text = bs.Lstr(value='${V}', subs=[('${V}', env['version'])])
            self.version = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'bottom',
                'hAttach': 'right',
                'hAlign': 'right',
                'flatness': 1.0,
                'vrDepth': -10,
                'shadow': 1.0 if vrMode else 0.5,
                'color': (1, 1, 1, 1) if vrMode else (0.5, 0.6, 0.5, 0.7),
                'scale': 0.9 if (interfaceType == 'small' or vrMode) else 0.7,
                'position': (-260, 10) if vrMode else (-10, 10),
                'text': text}))
            if not gDidInitialTransition:
                bs.animate(self.version.node, 'opacity', {2300: 0, 3000: 1.0})

        # throw in beta info..
        self.betaInfo = self.betaInfo2 = None
        if env['testBuild'] and not env['kioskMode']:
            self.betaInfo = bs.NodeActor(bs.newNode('text', attrs={
                'vAttach': 'center',
                'hAlign': 'center',
                'color': (1, 1, 1, 1),
                'shadow': 0.5,
                'flatness': 0.5,
                'scale': 1,
                'vrDepth': -60,
                'position': (230, 125) if env['kioskMode'] else (230, 35),
                'text': bs.Lstr(resource='testBuildText')}))
            if not gDidInitialTransition:
                bs.animate(self.betaInfo.node, 'opacity', {1300: 0, 1800: 1.0})

        model = bs.getModel('thePadLevel')
        treesModel = bs.getModel('trees')
        bottomModel = bs.getModel('thePadLevelBottom')
        testColorTexture = bs.getTexture('thePadLevelColor')
        treesTexture = bs.getTexture('treesColor')
        bgTex = bs.getTexture('menuBG')
        bgModel = bs.getModel('thePadBG')

        # (load these last since most platforms don't use them..)
        vrBottomFillModel = bs.getModel('thePadVRFillBottom')
        vrTopFillModel = bs.getModel('thePadVRFillTop')

        bsGlobals = bs.getSharedObject('globals')
        bsGlobals.cameraMode = 'rotate'

        if False:
            node = bs.newNode('timeDisplay', attrs={
                'timeMin': 2000,
                'timeMax': 10000,
                'showSubSeconds': True})
            self._fooText = bs.NodeActor(bs.newNode('text', attrs={
                'position': (0, -220),
                'flatness': 1.0,
                'hAlign': 'center'}))
            bsGlobals.connectAttr('gameTime', node, 'time2')
            node.connectAttr('output', self._fooText.node, 'text')

        tint = (1.14, 1.1, 1.0)
        bsGlobals.tint = tint

        bsGlobals.ambientColor = (1.06, 1.04, 1.03)
        bsGlobals.vignetteOuter = (0.45, 0.55, 0.54)
        bsGlobals.vignetteInner = (0.99, 0.98, 0.98)

        self.bottom = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': bottomModel,
            'lighting': False,
            'reflection': 'soft',
            'reflectionScale': [0.45],
            'colorTexture': testColorTexture}))
        self.vrBottomFill = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': vrBottomFillModel,
            'lighting': False,
            'vrOnly': True,
            'colorTexture': testColorTexture}))
        self.vrTopFill = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': vrTopFillModel,
            'vrOnly': True,
            'lighting': False,
            'colorTexture': bgTex}))
        self.terrain = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': model,
            'colorTexture': testColorTexture,
            'reflection': 'soft',
            'reflectionScale': [0.3]}))
        self.trees = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': treesModel,
            'lighting': False,
            'reflection': 'char',
            'reflectionScale': [0.1],
            'colorTexture': treesTexture}))
        self.bg = bs.NodeActor(bs.newNode('terrain', attrs={
            'model': bgModel,
            'color': (0.92, 0.91, 0.9),
            'lighting': False,
            'background': True,
            'colorTexture': bgTex}))
        textOffsetV = 0
        self._ts = 0.86

        self._language = None
        self._updateTimer = bs.Timer(1000, self._update, repeat=True)
        self._update()

        # hopefully this won't hitch but lets space these out anyway..
        bsInternal._addCleanFrameCallback(bs.WeakCall(self._startPreloads))

        random.seed()

        # on the main menu, also show our news..
        class News(object):

            def __init__(self, activity):
                self._valid = True
                self._messageDuration = 10000
                self._messageSpacing = 2000
                self._text = None
                self._activity = weakref.ref(activity)
                # if we're signed in, fetch news immediately..
                # otherwise wait until we are signed in
                self._fetchTimer = bs.Timer(1000,
                                            bs.WeakCall(self._tryFetchingNews),
                                            repeat=True)
                self._tryFetchingNews()

            # we now want to wait until we're signed in before fetching news
            def _tryFetchingNews(self):
                if bsInternal._getAccountState() == 'SIGNED_IN':
                    self._fetchNews()
                    self._fetchTimer = None

            def _fetchNews(self):
                try:
                    launchCount = bs.getConfig()['launchCount']
                except Exception:
                    launchCount = None
                global gLastNewsFetchTime
                gLastNewsFetchTime = time.time()

                # UPDATE - we now just pull news from MRVs
                news = bsInternal._getAccountMiscReadVal('n', None)
                if news is not None:
                    self._gotNews(news)

            def _changePhrase(self):

                global gLastNewsFetchTime

                # if our news is way out of date, lets re-request it..
                # otherwise, rotate our phrase
                if time.time() - gLastNewsFetchTime > 600.0:
                    self._fetchNews()
                    self._text = None
                else:
                    if self._text is not None:
                        if len(self._phrases) == 0:
                            for p in self._usedPhrases:
                                self._phrases.insert(0, p)
                        val = self._phrases.pop()
                        if val == '__ACH__':
                            vr = bs.getEnvironment()['vrMode']
                            bsUtils.Text(
                                bs.Lstr(resource='nextAchievementsText'),
                                color=(1, 1, 1, 1) if vr else (0.95, 0.9, 1, 0.4),
                                hostOnly=True,
                                maxWidth=200,
                                position=(-300, -35),
                                hAlign='right',
                                transition='fadeIn',
                                scale=0.9 if vr else 0.7,
                                flatness=1.0 if vr else 0.6,
                                shadow=1.0 if vr else 0.5,
                                hAttach="center",
                                vAttach="top",
                                transitionDelay=1000,
                                transitionOutDelay=self._messageDuration) \
                                .autoRetain()
                            import bsAchievement
                            achs = [a for a in bsAchievement.gAchievements
                                    if not a.isComplete()]
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(4, len(achs))))
                                a.createDisplay(-180, -35, 1000,
                                                outDelay=self._messageDuration,
                                                style='news')
                            if len(achs) > 0:
                                a = achs.pop(random.randrange(min(8, len(achs))))
                                a.createDisplay(180, -35, 1250,
                                                outDelay=self._messageDuration,
                                                style='news')
                        else:
                            s = self._messageSpacing
                            keys = {s: 0, s + 1000: 1.0,
                                    s + self._messageDuration - 1000: 1.0,
                                    s + self._messageDuration: 0.0}
                            bs.animate(self._text.node, "opacity",
                                       dict([[k, v] for k, v in keys.items()]))
                            self._text.node.text = val

            def _gotNews(self, news):

                # run this stuff in the context of our activity since we need
                # to make nodes and stuff.. should fix the serverGet call so it
                activity = self._activity()
                if activity is None or activity.isFinalized(): return
                with bs.Context(activity):
                    self._phrases = []
                    # show upcoming achievements in non-vr versions
                    # (currently too hard to read in vr)
                    self._usedPhrases = (
                                            ['__ACH__'] if not bs.getEnvironment()['vrMode']
                                            else []) + [s for s in news.split('<br>\n') if s != '']
                    self._phraseChangeTimer = bs.Timer(
                        self._messageDuration + self._messageSpacing,
                        bs.WeakCall(self._changePhrase), repeat=True)

                    sc = 1.2 if (bs.getEnvironment()['interfaceType'] == 'small'
                                 or bs.getEnvironment()['vrMode']) else 0.8

                    self._text = bs.NodeActor(bs.newNode('text', attrs={
                        'vAttach': 'top',
                        'hAttach': 'center',
                        'hAlign': 'center',
                        'vrDepth': -20,
                        'shadow': 1.0 if bs.getEnvironment()['vrMode'] else 0.4,
                        'flatness': 0.8,
                        'vAlign': 'top',
                        'color': ((1, 1, 1, 1) if bs.getEnvironment()['vrMode']
                                  else (0.7, 0.65, 0.75, 1.0)),
                        'scale': sc,
                        'maxWidth': 900.0 / sc,
                        'position': (0, -10)}))
                    self._changePhrase()

        if not env['kioskMode'] and not env.get('toolbarTest', True):
            self._news = News(self)

        # bring up the last place we were, or start at the main menu otherwise
        with bs.Context('UI'):
            try:
                mainWindow = bsUI.gMainWindow
            except Exception:
                mainWindow = None

            # when coming back from a kiosk-mode game, jump to
            # the kiosk start screen.. if bsUtils.gRunningKioskModeGame:
            if bs.getEnvironment()['kioskMode']:
                bsUI.uiGlobals['mainMenuWindow'] = \
                    bsUI.KioskWindow().getRootWidget()
            # ..or in normal cases go back to the main menu
            else:
                if mainWindow == 'AccessoriesManager':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        accManager.AccManagerWindow(transition=None).getRootWidget()
                elif mainWindow == 'Gather':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.GatherWindow(transition=None).getRootWidget()
                elif mainWindow == 'Watch':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.WatchWindow(transition=None).getRootWidget()
                elif mainWindow == 'Team Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.TeamsSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Free-for-All Game Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.TeamsWindow(sessionType=bs.FreeForAllSession,
                                         transition=None).getRootWidget()
                elif mainWindow == 'Coop Select':
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.CoopWindow(transition=None).getRootWidget()
                else:
                    bsUI.uiGlobals['mainMenuWindow'] = \
                        bsUI.MainMenuWindow(transition=None).getRootWidget()

                # attempt to show any pending offers immediately.
                # If that doesn't work, try again in a few seconds
                # (we may not have heard back from the server)
                # ..if that doesn't work they'll just have to wait
                # until the next opportunity.
                if not bsUI._showOffer():
                    def tryAgain():
                        if not bsUI._showOffer():
                            # try one last time..
                            bs.realTimer(2000, bsUI._showOffer)

                    bs.realTimer(2000, tryAgain)

        gDidInitialTransition = True


bsMainMenu.MainMenuActivity = NewMainMenuActivity


class NewMainMenuWindow(MainMenuWindow):
    def _refresh(self):

        # clear everything that was there..
        children = self._rootWidget.getChildren()
        for c in children:
            c.delete()

        # alter some default behavior when going through the main menu..
        if not self._inGame:
            bsUtils.gRunningKioskModeGame = False

        # useAutoSelect = False if self._inGame else True
        useAutoSelect = True

        buttonHeight = 45
        buttonWidth = 200
        padding = 10

        tDelay = 0
        tDelayInc = 0
        tDelayPlay = 0

        is_kiosk = bs.getEnvironment()['kioskMode']

        self._r = 'mainMenu'

        env = bs.getEnvironment()
        self._haveQuitButton = (
                env['interfaceType'] == 'large' or bsInternal._isOuyaBuild(
        ) or (env['platform'] == 'windows'
              and env['subplatform'] == 'oculus'))

        self._haveStoreButton = True if not self._inGame else False

        self._haveSettingsButton = True if ((not self._inGame or not env.get(
            'toolbarTest', True)) and not is_kiosk) else False

        self._inputDevice = inputDevice = bsInternal._getUIInputDevice()
        self._inputPlayer = (inputDevice.getPlayer()
                             if inputDevice is not None else None)
        if self._inputPlayer is not None and not self._inputPlayer.exists():
            self._inputPlayer = None
        self._connectedToRemotePlayer = inputDevice.isConnectedToRemotePlayer(
        ) if inputDevice is not None else False

        positions = []
        pIndex = 0

        if self._inGame:

            customMenuEntries = []
            session = bsInternal._getForegroundHostSession()
            if session is not None:
                try:
                    customMenuEntries = session.getCustomMenuEntries()
                    for c in customMenuEntries:
                        if (type(c) is not dict or not 'label' in c
                                or type(c['label']) not in (str, unicode, bs.Lstr)
                                or 'call' not in c or not callable(c['call'])):
                            raise Exception(
                                "invalid custom menu entry: " + str(c))
                except Exception:
                    customMenuEntries = []
                    bs.printException(
                        'exception getting custom menu entries for', session)

            self._width = 250
            self._height = 250 if self._inputPlayer is not None else 180
            if is_kiosk and self._inputPlayer is not None: self._height -= 40
            if not self._haveSettingsButton:
                self._height -= 50
            if self._connectedToRemotePlayer:
                # in this case we have a leave *and* a disconnect button
                self._height += 50
            self._height += 50 * (len(customMenuEntries))
            bs.containerWidget(
                edit=self._rootWidget, size=(self._width, self._height),
                scale=2.15 if gSmallUI else 1.6 if gMedUI else 1.0)
            h = 125
            v = (self._height - 80 if self._inputPlayer is not None
                 else self._height - 60)
            hOffset = 0
            dhOffset = 0
            vOffset = -50
            for i in range(6 + len(customMenuEntries)):
                positions.append((h, v, 1.0))
                v += vOffset
                h += hOffset
                hOffset += dhOffset

        # not in game
        else:
            global gDidMenuIntro
            if gDidMenuIntro == False:
                tDelay = 2000
                tDelayInc = 20
                tDelayPlay = 1700
                gDidMenuIntro = True

            self._width = 400
            self._height = 200

            accountType = bsInternal._getAccountType(
            ) if bsInternal._getAccountState() == 'SIGNED_IN' else None
            enableAccountButton = True

            if bsInternal._getAccountState() == 'SIGNED_IN':
                accountTypeName = bsInternal._getAccountDisplayString()
                accountTypeIcon = None
                accountTextColor = (1, 1, 1)
            else:
                accountTypeName = bs.Lstr(
                    resource='notSignedInText',
                    fallbackResource='accountSettingsWindow.titleText')
                accountTypeIcon = None
                accountTextColor = (1, 0.2, 0.2)
            accountTypeIconColor = (1, 1, 1)
            accountTypeCall = self._showAccountWindow
            accountTypeEnableButtonSound = True

            bCount = 4  # play, help, credits, settings
            if enableAccountButton:
                bCount += 1
            if self._haveQuitButton:
                bCount += 1
            if self._haveStoreButton:
                bCount += 1

            if gSmallUI:
                rootWidgetScale = 1.6
                playButtonWidth = buttonWidth * 0.65
                playButtonHeight = buttonHeight * 1.1
                smallButtonScale = 0.51 if bCount > 6 else 0.63
                buttonYOffs = -20
                buttonYOffs2 = -60
                buttonHeight *= 1.3
                buttonSpacing = 1.04
            elif gMedUI:
                rootWidgetScale = 1.3
                playButtonWidth = buttonWidth * 0.65
                playButtonHeight = buttonHeight * 1.1
                smallButtonScale = 0.6
                buttonYOffs = -55
                buttonYOffs2 = -75
                buttonHeight *= 1.25
                buttonSpacing = 1.1
            else:
                rootWidgetScale = 1.0
                playButtonWidth = buttonWidth * 0.65
                playButtonHeight = buttonHeight * 1.1
                smallButtonScale = 0.75
                buttonYOffs = -80
                buttonYOffs2 = -100
                buttonHeight *= 1.2
                buttonSpacing = 1.1

            spc = buttonWidth * smallButtonScale * buttonSpacing

            bs.containerWidget(
                edit=self._rootWidget, size=(self._width, self._height),
                background=False, scale=rootWidgetScale)

            positions = [[self._width * 0.5, buttonYOffs, 1.7]]
            xOffs = self._width * 0.5 - (spc * (bCount - 1) * 0.5) + (spc * 0.5)
            for i in range(bCount - 1):
                positions.append(
                    [xOffs + spc * i - 1.0, buttonYOffs + buttonYOffs2,
                     smallButtonScale])

        if not self._inGame:

            # in kiosk mode, provide a button to get back to the kiosk menu
            if bs.getEnvironment()['kioskMode']:
                h, v, scale = positions[pIndex]
                thisBWidth = buttonWidth * 0.4 * scale
                demoMenuDelay = 0 if tDelayPlay == 0 else max(0, tDelayPlay + 100)
                self._demoMenuButton = bs.buttonWidget(
                    parent=self._rootWidget,
                    position=(self._width * 0.5 - thisBWidth * 0.5, v + 90),
                    size=(thisBWidth, 45),
                    autoSelect=True, color=(0.45, 0.55, 0.45),
                    textColor=(0.7, 0.8, 0.7),
                    label=bs.Lstr(resource=self._r + '.demoMenuText'),
                    transitionDelay=demoMenuDelay,
                    onActivateCall=self._demoMenuPress)
            else:
                self._demoMenuButton = None

            foo = -1 if gSmallUI else 1 if gMedUI else 3

            h, v, scale = positions[pIndex]
            v = v + foo
            gatherDelay = 0 if tDelayPlay == 0 else max(0, tDelayPlay + 100)
            thisH = h - playButtonWidth * 0.5 * scale - 40 * scale
            thisBWidth = buttonWidth * 0.25 * scale
            thisBHeight = buttonHeight * 0.82 * scale
            self._gatherButton = b = bs.buttonWidget(
                parent=self._rootWidget, position=(thisH - thisBWidth * 0.5, v),
                size=(thisBWidth, thisBHeight),
                autoSelect=useAutoSelect, buttonType='square', label='',
                transitionDelay=gatherDelay, onActivateCall=self._gatherPress)
            bs.textWidget(parent=self._rootWidget,
                          position=(thisH, v + buttonHeight * 0.33),
                          size=(0, 0),
                          scale=0.75,
                          transitionDelay=gatherDelay,
                          drawController=b,
                          color=(0.75, 1.0, 0.7),
                          maxWidth=buttonWidth * 0.33,
                          text=bs.Lstr(resource='gatherWindow.titleText'),
                          hAlign='center', vAlign='center')
            iconSize = thisBWidth * 0.6
            bs.imageWidget(parent=self._rootWidget, size=(iconSize, iconSize),
                           drawController=b,
                           transitionDelay=gatherDelay,
                           position=(thisH - 0.5 * iconSize, v + 0.31 * thisBHeight),
                           texture=bs.getTexture('usersButton'))

            # Accessories Manager Window
            self._accButton = b = bs.buttonWidget(
                parent=self._rootWidget, position=(thisH - thisBWidth * 0.5 - 90, v),
                size=(thisBWidth, thisBHeight),
                autoSelect=useAutoSelect, buttonType='square', label='',
                transitionDelay=gatherDelay, onActivateCall=self._accPress)
            bs.textWidget(parent=self._rootWidget,
                          position=(thisH - 90, v + buttonHeight * 0.33),
                          size=(0, 0),
                          scale=0.75,
                          transitionDelay=gatherDelay,
                          drawController=b,
                          color=(0.75, 1.0, 0.7),
                          maxWidth=buttonWidth * 0.33,
                          text=bs.Lstr(value="Accessories Manager"),
                          hAlign='center', vAlign='center')
            iconSize = thisBWidth * 0.6
            bs.imageWidget(parent=self._rootWidget, size=(iconSize, iconSize),
                           drawController=b,
                           transitionDelay=gatherDelay,
                           position=(thisH - 0.5 * iconSize - 90, v + 0.31 * thisBHeight),
                           texture=bs.getTexture('inventoryIcon'))

            # play button
            h, v, scale = positions[pIndex]
            pIndex += 1
            self._startButton = startButton = b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h - playButtonWidth * 0.5 * scale, v),
                size=(playButtonWidth, playButtonHeight),
                autoSelect=useAutoSelect, scale=scale, textResScale=2.0,
                label=bs.Lstr(resource='playText'),
                transitionDelay=tDelayPlay, onActivateCall=self._playPress)

            bs.containerWidget(
                edit=self._rootWidget, startButton=startButton,
                selectedChild=startButton)

            v = v + foo

            watchDelay = 0 if tDelayPlay == 0 else max(0, tDelayPlay - 100)
            thisH = h + playButtonWidth * 0.5 * scale + 40 * scale
            thisBWidth = buttonWidth * 0.25 * scale
            thisBHeight = buttonHeight * 0.82 * scale
            self._watchButton = b = bs.buttonWidget(
                parent=self._rootWidget, position=(thisH - thisBWidth * 0.5, v),
                size=(thisBWidth, thisBHeight),
                autoSelect=useAutoSelect, buttonType='square', label='',
                transitionDelay=watchDelay, onActivateCall=self._watchPress)

            bs.textWidget(parent=self._rootWidget,
                          position=(thisH, v + buttonHeight * 0.33),
                          size=(0, 0),
                          scale=0.75,
                          transitionDelay=watchDelay,
                          color=(0.75, 1.0, 0.7),
                          drawController=b,
                          maxWidth=buttonWidth * 0.33,
                          text=bs.Lstr(resource='watchWindow.titleText'),
                          hAlign='center', vAlign='center')
            iconSize = thisBWidth * 0.55
            bs.imageWidget(parent=self._rootWidget, size=(iconSize, iconSize),
                           drawController=b,
                           transitionDelay=watchDelay,
                           position=(thisH - 0.5 * iconSize, v + 0.33 * thisBHeight),
                           texture=bs.getTexture('tv'))

            if not self._inGame and enableAccountButton:
                thisBWidth = buttonWidth
                h, v, scale = positions[pIndex]
                pIndex += 1
                self._gcButton = gcButton = b = bs.buttonWidget(
                    parent=self._rootWidget,
                    position=(h - thisBWidth * 0.5 * scale, v),
                    size=(thisBWidth, buttonHeight),
                    scale=scale, label=accountTypeName,
                    autoSelect=useAutoSelect, onActivateCall=accountTypeCall,
                    textColor=accountTextColor, icon=accountTypeIcon,
                    iconColor=accountTypeIconColor, transitionDelay=tDelay,
                    enableSound=accountTypeEnableButtonSound)

                # scattered eggs on easter
                if bsInternal._getAccountMiscReadVal(
                        'easter', False) and not self._inGame:
                    iconSize = 32
                    iw = bs.imageWidget(parent=self._rootWidget,
                                        position=(h - iconSize * 0.5 + 35, v +
                                                  buttonHeight * scale -
                                                  iconSize * 0.24 + 1.5),
                                        transitionDelay=tDelay,
                                        size=(iconSize, iconSize),
                                        texture=bs.getTexture('egg2'),
                                        tiltScale=0.0)
                tDelay += tDelayInc
            else:
                self._gcButton = None

            # how-to-play button
            h, v, scale = positions[pIndex]
            pIndex += 1
            self._howToPlayButton = howToPlayButton = b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h - buttonWidth * 0.5 * scale, v),
                scale=scale, autoSelect=useAutoSelect,
                size=(buttonWidth, buttonHeight),
                label=bs.Lstr(resource=self._r + '.howToPlayText'),
                transitionDelay=tDelay, onActivateCall=self._howToPlay)

            # scattered eggs on easter
            if bsInternal._getAccountMiscReadVal(
                    'easter', False) and not self._inGame:
                iconSize = 28
                iw = bs.imageWidget(
                    parent=self._rootWidget,
                    position=(h - iconSize * 0.5 + 30,
                              v + buttonHeight * scale -
                              iconSize * 0.24 + 1.5),
                    transitionDelay=tDelay, size=(iconSize, iconSize),
                    texture=bs.getTexture('egg4'),
                    tiltScale=0.0)

            # credits button
            tDelay += tDelayInc
            h, v, scale = positions[pIndex]
            pIndex += 1
            self._creditsButton = creditsButton = b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h - buttonWidth * 0.5 * scale, v),
                size=(buttonWidth, buttonHeight), autoSelect=useAutoSelect,
                label=bs.Lstr(
                    resource=self._r + '.creditsText'),
                scale=scale,
                transitionDelay=tDelay,
                onActivateCall=self._credits)
            tDelay += tDelayInc

        # in-game
        else:
            self._startButton = None
            pause()

            # (player name if applicable)
            if self._inputPlayer is not None:
                playerName = self._inputPlayer.getName()
                h, v, scale = positions[pIndex]
                v += 35
                b = bs.textWidget(
                    parent=self._rootWidget, position=(h - buttonWidth / 2, v),
                    size=(buttonWidth, buttonHeight),
                    color=(1, 1, 1, 0.5),
                    scale=0.7, hAlign='center', text=bs.Lstr(
                        value=playerName))
            else:
                playerName = ''

            h, v, scale = positions[pIndex]
            pIndex += 1

            b = bs.buttonWidget(
                parent=self._rootWidget, position=(h - buttonWidth / 2, v),
                size=(buttonWidth, buttonHeight),
                scale=scale, label=bs.Lstr(
                    resource=self._r + '.resumeText'),
                autoSelect=useAutoSelect, onActivateCall=self._resume)
            bs.containerWidget(edit=self._rootWidget, cancelButton=b)

            # add any custom options defined by the current game
            for entry in customMenuEntries:
                h, v, scale = positions[pIndex]
                pIndex += 1

                # ask the entry whether we should resume when we call
                # it (defaults to true)
                try:
                    resume = entry['resumeOnCall']
                except Exception:
                    resume = True

                if resume:
                    call = bs.Call(self._resumeAndCall, entry['call'])
                else:
                    call = bs.Call(entry['call'], bs.WeakCall(self._resume))

                b = bs.buttonWidget(parent=self._rootWidget,
                                    position=(h - buttonWidth / 2, v),
                                    size=(buttonWidth, buttonHeight),
                                    scale=scale, onActivateCall=call,
                                    label=entry['label'],
                                    autoSelect=useAutoSelect)

            # add a 'leave' button if the menu-owner has a player
            if ((self._inputPlayer is not None or self._connectedToRemotePlayer)
                    and not is_kiosk):
                h, v, scale = positions[pIndex]
                pIndex += 1
                b = bs.buttonWidget(parent=self._rootWidget,
                                    position=(h - buttonWidth / 2, v),
                                    size=(buttonWidth, buttonHeight),
                                    scale=scale, onActivateCall=self._leave,
                                    label='', autoSelect=useAutoSelect)

                if (playerName != '' and playerName[0] != '<'
                        and playerName[-1] != '>'):
                    t = bs.Lstr(resource=self._r + '.justPlayerText',
                                subs=[('${NAME}', playerName)])
                else:
                    t = bs.Lstr(value=playerName)
                    # t = playerName
                bs.textWidget(
                    parent=self._rootWidget,
                    position=(h, v + buttonHeight *
                              (0.64 if playerName != '' else 0.5)),
                    size=(0, 0),
                    text=bs.Lstr(resource=self._r + '.leaveGameText'),
                    scale=(0.83 if playerName != '' else 1.0),
                    color=(0.75, 1.0, 0.7),
                    hAlign='center', vAlign='center', drawController=b,
                    maxWidth=buttonWidth * 0.9)
                bs.textWidget(
                    parent=self._rootWidget,
                    position=(h, v + buttonHeight * 0.27),
                    size=(0, 0),
                    text=t, color=(0.75, 1.0, 0.7),
                    hAlign='center', vAlign='center', drawController=b,
                    scale=0.45, maxWidth=buttonWidth * 0.9)

        if self._haveSettingsButton:
            h, v, scale = positions[pIndex]
            pIndex += 1
            self._settingsButton = settingsButton = b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h - buttonWidth * 0.5 * scale, v),
                size=(buttonWidth, buttonHeight),
                scale=scale, autoSelect=useAutoSelect, label=bs.Lstr(
                    resource=self._r + '.settingsText'),
                transitionDelay=tDelay, onActivateCall=self._settings)

        # scattered eggs on easter
        if bsInternal._getAccountMiscReadVal(
                'easter', False) and not self._inGame:
            iconSize = 34
            iw = bs.imageWidget(
                parent=self._rootWidget,
                position=(h - iconSize * 0.5 - 15, v + buttonHeight * scale -
                          iconSize * 0.24 + 1.5),
                transitionDelay=tDelay, size=(iconSize, iconSize),
                texture=bs.getTexture('egg3'),
                tiltScale=0.0)

        tDelay += tDelayInc

        if self._inGame:
            h, v, scale = positions[pIndex]
            pIndex += 1

            # if we're in a replay, we have a 'Leave Replay' button
            if bsInternal._isInReplay():
                b = bs.buttonWidget(
                    parent=self._rootWidget,
                    position=(h - buttonWidth * 0.5 * scale, v),
                    scale=scale, size=(buttonWidth, buttonHeight),
                    autoSelect=useAutoSelect, label=bs.Lstr(
                        resource='replayEndText'),
                    onActivateCall=self._confirmEndReplay)
            elif bsInternal._getForegroundHostSession() is not None:
                b = bs.buttonWidget(
                    parent=self._rootWidget,
                    position=(h - buttonWidth * 0.5 * scale, v),
                    scale=scale, size=(buttonWidth, buttonHeight),
                    autoSelect=useAutoSelect, label=bs.Lstr(
                        resource=self._r + '.endGameText'),
                    onActivateCall=self._confirmEndGame)
            # assume we're in a client-session..
            else:
                b = bs.buttonWidget(
                    parent=self._rootWidget,
                    position=(h - buttonWidth * 0.5 * scale, v),
                    scale=scale, size=(buttonWidth, buttonHeight),
                    autoSelect=useAutoSelect, label=bs.Lstr(
                        resource=self._r + '.leavePartyText'),
                    onActivateCall=self._confirmLeaveParty)

        if self._haveStoreButton:
            thisBWidth = buttonWidth
            h, v, scale = positions[pIndex]
            pIndex += 1

            sb = self._storeButtonInstance = StoreButton(
                parent=self._rootWidget,
                position=(h - thisBWidth * 0.5 * scale, v),
                size=(thisBWidth, buttonHeight),
                scale=scale, onActivateCall=bs.WeakCall(self._onStorePressed),
                saleScale=1.3, transitionDelay=tDelay)
            self._storeButton = storeButton = sb.getButtonWidget()
            iconSize = 55 if gSmallUI else 55 if gMedUI else 70
            iw = bs.imageWidget(
                parent=self._rootWidget,
                position=(h - iconSize * 0.5,
                          v + buttonHeight * scale - iconSize * 0.23),
                transitionDelay=tDelay, size=(iconSize, iconSize),
                texture=bs.getTexture(self._storeCharTex),
                tiltScale=0.0, drawController=storeButton)

            tDelay += tDelayInc
        else:
            self._storeButton = None

        if not self._inGame and self._haveQuitButton:
            h, v, scale = positions[pIndex]
            pIndex += 1
            self._quitButton = quitButton = b = bs.buttonWidget(
                parent=self._rootWidget, autoSelect=useAutoSelect,
                position=(h - buttonWidth * 0.5 * scale, v),
                size=(buttonWidth, buttonHeight),
                scale=scale, label=bs.Lstr(
                    resource=self._r +
                             ('.quitText'
                              if 'Mac' in bs.getEnvironment()['userAgentString'] else
                              '.exitGameText')),
                onActivateCall=self._quit, transitionDelay=tDelay)

            # scattered eggs on easter
            if bsInternal._getAccountMiscReadVal('easter', False):
                iconSize = 30
                iw = bs.imageWidget(
                    parent=self._rootWidget,
                    position=(h - iconSize * 0.5 + 25,
                              v + buttonHeight * scale - iconSize * 0.24 + 1.5),
                    transitionDelay=tDelay, size=(iconSize, iconSize),
                    texture=bs.getTexture('egg1'),
                    tiltScale=0.0)

            # if bsInternal._isOuyaBuild() or _bs._isRunningOnFireTV():
            bs.containerWidget(edit=self._rootWidget, cancelButton=quitButton)
            tDelay += tDelayInc
        else:
            self._quitButton = None

            # if we're not in-game, have no quit button, and this is android,
            # we want back presses to quit our activity
            if (not self._inGame and not self._haveQuitButton
                    and 'android' in bs.getEnvironment()['userAgentString']):
                bs.containerWidget(edit=self._rootWidget, onCancelCall=bs.Call(
                    QuitWindow, swish=True, back=True))

        # add speed-up/slow-down buttons for replays
        # (ideally this should be part of a fading-out playback bar like most
        # media players but this works for now)
        if bsInternal._isInReplay():
            bSize = 50
            bBuffer = 10
            tScale = 0.75
            if gSmallUI:
                bSize *= 0.6
                bBuffer *= 1.0
                vOffs = -40
                tScale = 0.5
            elif gMedUI:
                vOffs = -70
            else:
                vOffs = -100
            self._replaySpeedText = bs.textWidget(
                parent=self._rootWidget, text=bs.Lstr(
                    resource='watchWindow.playbackSpeedText',
                    subs=[('${SPEED}', str(1.23))]),
                position=(h, v + vOffs + 7 * tScale),
                hAlign='center', vAlign='center', size=(0, 0),
                scale=tScale)
            # update to current value
            self._changeReplaySpeed(0)
            # keep updating in a timer in case it gets changed elsewhere
            self._changeReplaySpeedTimer = bs.Timer(
                250, bs.WeakCall(self._changeReplaySpeed, 0),
                timeType='real', repeat=True)
            b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h - bSize - bBuffer, v - bSize - bBuffer + vOffs),
                buttonType='square', size=(bSize, bSize),
                label='', autoSelect=True, onActivateCall=bs.Call(
                    self._changeReplaySpeed, -1))
            bs.textWidget(
                parent=self._rootWidget, drawController=b, text='-',
                position=(h - bSize * 0.5 - bBuffer,
                          v - bSize * 0.5 - bBuffer + 5 * tScale + vOffs),
                hAlign='center', vAlign='center', size=(0, 0),
                scale=3.0 * tScale)
            b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(h + bBuffer, v - bSize - bBuffer + vOffs),
                buttonType='square', size=(bSize, bSize),
                label='', autoSelect=True, onActivateCall=bs.Call(
                    self._changeReplaySpeed, 1))
            bs.textWidget(
                parent=self._rootWidget, drawController=b, text='+',
                position=(h + bSize * 0.5 + bBuffer,
                          v - bSize * 0.5 - bBuffer + 5 * tScale + vOffs),
                hAlign='center', vAlign='center', size=(0, 0),
                scale=3.0 * tScale)

    def _save_state(self):
        # dont do this for the in-game menu..
        if self._inGame:
            return
        global _gMainMenuSelection
        s = self._rootWidget.getSelectedChild()
        if s == self._startButton:
            _gMainMenuSelection = 'Start'
        elif s == self._gatherButton:
            _gMainMenuSelection = 'Gather'
        elif s == self._accButton:
            _gMainMenuSelection = 'AccessoriesManager'
        elif s == self._watchButton:
            _gMainMenuSelection = 'Watch'
        elif s == self._howToPlayButton:
            _gMainMenuSelection = 'HowToPlay'
        elif s == self._creditsButton:
            _gMainMenuSelection = 'Credits'
        elif s == self._settingsButton:
            _gMainMenuSelection = 'Settings'
        elif s == self._gcButton:
            _gMainMenuSelection = 'GameService'
        elif s == self._storeButton:
            _gMainMenuSelection = 'Store'
        elif s == self._quitButton:
            _gMainMenuSelection = 'Quit'
        elif s == self._demoMenuButton:
            _gMainMenuSelection = 'DemoMenu'
        else:
            print 'unknown widget in main menu store selection:'
            _gMainMenuSelection = 'Start'

    def _restore_state(self):
        # dont do this for the in-game menu..
        if self._inGame:
            return
        global _gMainMenuSelection
        try:
            selName = _gMainMenuSelection
        except Exception:
            selName = 'Start'
        if selName == 'HowToPlay':
            sel = self._howToPlayButton
        elif selName == 'Gather':
            sel = self._gatherButton
        elif selName == 'AccessoriesManager':
            sel = self._accButton
        elif selName == 'Watch':
            sel = self._watchButton
        elif selName == 'Credits':
            sel = self._creditsButton
        elif selName == 'Settings':
            sel = self._settingsButton
        elif selName == 'GameService':
            sel = self._gcButton
        elif selName == 'Store':
            sel = self._storeButton
        elif selName == 'Quit':
            sel = self._quitButton
        elif selName == 'DemoMenu':
            sel = self._demoMenuButton
        else:
            sel = self._startButton
        if sel is not None:
            bs.containerWidget(edit=self._rootWidget, selectedChild=sel)

    def _accPress(self):

        self._save_state()
        bs.containerWidget(edit=self._rootWidget, transition='outLeft')
        uiGlobals['mainMenuWindow'] = accManager.AccManagerWindow(
            originWidget=self._accButton, backLocationCls=NewMainMenuWindow).getRootWidget()
bsUI.MainMenuWindow = NewMainMenuWindow