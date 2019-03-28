from __future__ import print_function
import bs
import bsInternal
import os
import urllib
import urllib2
import httplib
import json
import random
import time
import threading
import weakref
from md5 import md5
from bsUI import gSmallUI, gMedUI, gHeadingColor, uiGlobals, ConfirmWindow, StoreWindow, MainMenuWindow, Window
from functools import partial
from accAssistor import TextWidget, ContainerWidget, ButtonWidget, CheckBoxWidget, ScrollWidget, ColumnWidget, Widget


# roll own uuid4 implementation because uuid module might not be available
# this is broken on android/1.4.216 due to 16**8 == 0 o.O
def uuid4():
    components = [8, 4, 4, 4, 12]
    return "-".join([('%012x' % random.randrange(16 ** a))[12 - a:] for a in components])


modPath = bs.getEnvironment()['userScriptsDirectory'] + "/"
PROTOCOL_VERSION = 1.0
STAT_SERVER_URI = None  # currently https://stat-server.bs-oam.tk is being built for it
SUPPORTS_HTTPS = hasattr(httplib, 'HTTPS')
USER_REPO = "I-Am-The-Great/BombSquad-Official-Accessory-Archive"

_supports_auto_reloading = True
_auto_reloader_type = "patching"
StoreWindow_setTab = StoreWindow._setTab
MainMenuWindow__init__ = MainMenuWindow.__init__


def bsGetAPIVersion():
    return 4


quittoapply = None
checkedMainMenu = False

if 'acc_manager_config' not in bs.getConfig():
    bs.getConfig()['acc_manager_config'] = {}
    bs.writeConfig()

config = bs.getConfig()['acc_manager_config']


def index_url(branch=None):
    if not branch:
        branch = config.get("branch", "master")
    if SUPPORTS_HTTPS:
        yield "https://raw.githubusercontent.com/{}/{}/index.json".format(USER_REPO, branch)
    yield "http://raw.githack.com/{}/{}/index.json".format(USER_REPO, branch)


def file_url(data, fileto=None):
    if "commit_sha" in data and "filename" in data:
        commit_hexsha = data["commit_sha"]
        filename = data["filename"]
        yield "http://rawcdn.githack.com/{}/{}/all-files/{}".format(USER_REPO, commit_hexsha, filename)
    else:
        raise RuntimeError("Invalid accessory, " + data["name"])


def try_fetch_cb(generator, callback, **kwargs):
    def f(data, status_code):
        if data:
            callback(data, status_code)
        else:
            try:
                get_cached(next(generator), f, **kwargs)
            except StopIteration:
                callback(None, None)

    get_cached(next(generator), f, **kwargs)


web_cache = config.get("web_cache", {})
config["web_cache"] = web_cache

if STAT_SERVER_URI and 'uuid' not in config:
    config['uuid'] = uuid4()
    bs.writeConfig()


def get_cached(url, callback, force_fresh=False, fallback_to_outdated=True):
    def cache(data, status_code):
        if data:
            web_cache[url] = (data, time.time())
            bs.writeConfig()

    def f(data, status_code):
        # TODO: cancel prev fetchs
        callback(data, status_code)
        cache(data, status_code)

    if force_fresh:
        acc_serverGet(url, {}, f)
        return

    if url in web_cache:
        data, timestamp = web_cache[url]
        if timestamp + 10 * 30 > time.time():
            acc_serverGet(url, {}, cache)
        if fallback_to_outdated or timestamp + 10 * 60 > time.time():
            callback(data, None)
            return

    acc_serverGet(url, {}, f)


def get_index(callback, branch=None, **kwargs):
    try_fetch_cb(index_url(branch), callback, **kwargs)


def fetch_stats(callback, **kwargs):
    if STAT_SERVER_URI:
        url = STAT_SERVER_URI + "/stats?uuid=" + config['uuid']
        get_cached(url, callback, **kwargs)


def stats_cached():
    if not STAT_SERVER_URI:
        return False
    url = STAT_SERVER_URI + "/stats?uuid=" + config['uuid']
    return url in web_cache


def submit_file_rating(file, rating, callback):
    if not STAT_SERVER_URI:
        return bs.screenMessage('rating submission disabled')
    url = STAT_SERVER_URI + "/submit_rating"
    data = {
        "uuid": config['uuid'],
        "file_str": file.name,
        "rating": rating,
    }

    def cb(data, status_code):
        if status_code == 200:
            bs.screenMessage("rating submitted")
            callback()
        else:
            bs.screenMessage("failed to submit rating")

    acc_serverPost(url, data, cb, eval_data=False)


def submit_download(file):
    if not config.get('submit-download-statistics', True) or not STAT_SERVER_URI:
        return

    url = STAT_SERVER_URI + "/submit_download"
    data = {
        "uuid": config.get('uuid'),
        "file_str": file.name,
    }

    def cb(data, status_code):
        if status_code != 200:
            print("failed to submit download stats")

    acc_serverPost(url, data, cb, eval_data=False)


def fetch_file(data, callback):
    generator = file_url(data)

    def f(data, status_code):
        if data:
            callback(data, status_code)
        else:
            try:
                acc_serverGet(next(generator), {}, f, eval_data=False)
            except StopIteration:
                callback(None, None)

    acc_serverGet(next(generator), {}, f, eval_data=False)


def process_server_data(data):
    version = data["version"]
    if version > PROTOCOL_VERSION:
        print("version diff:", version, PROTOCOL_VERSION)
        if version >= data["least-to-work"]:
            return RedownloadAccInstaller()
        bs.screenMessage("there is a new update available for the accessories manager")
    files = data["all-files"]
    contributors = data["contributors"]
    return files, contributors, version


def _cb_checkUpdateData(self, data, status_code):
    try:
        if data:
            f, c, v = process_server_data(data)
            files = [File(d) for d in f.values()]
            for file in files:
                file._files = {m.base: m for m in files}
                if file.is_installed() and file.is_outdated():
                    if config.get("auto-update-old-file", True):
                        bs.screenMessage("updating file '{}'...".format(file.name))

                        def cb(file, success):
                            if success:
                                bs.screenMessage("updated file '{}'.".format(file.name))

                        file.install(cb)
                    else:
                        bs.screenMessage("an update for file '{}' is available!".format(file.name))
    except:
        bs.printException()
        bs.screenMessage("failed to check for file updates")


oldMainInit = MainMenuWindow.__init__


def newMainInit(self, transition='inRight'):
    global checkedMainMenu
    oldMainInit(self, transition)
    if checkedMainMenu:
        return
    checkedMainMenu = True
    if config.get("auto-check-updates", True):
        get_index(self._acc_checkUpdateData, force_fresh=True)


MainMenuWindow.__init__ = newMainInit
MainMenuWindow._acc_checkUpdateData = _cb_checkUpdateData


class AccManager_ServerCallThread(threading.Thread):

    def __init__(self, request, requestType, data, callback, eval_data=True):
        threading.Thread.__init__(self)
        self._request = request.encode("ascii")  # embedded python2.7 has weird encoding issues
        self._requestType = requestType
        self._data = {} if data is None else data
        self._eval_data = eval_data
        self._callback = callback

        self._context = bs.Context('current')

        # save and restore the context we were created from
        activity = bs.getActivity(exceptionOnNone=False)
        self._activity = weakref.ref(activity) if activity is not None else None

    def _runCallback(self, *args):

        # if we were created in an activity context and that activity has since died, do nothing
        # (hmm should we be using a context-call instead of doing this manually?)
        if self._activity is not None and (self._activity() is None or self._activity().isFinalized()):
            return

        # (technically we could do the same check for session contexts, but not gonna worry about it for now)
        with self._context:
            self._callback(*args)

    def run(self):
        try:
            bsInternal._setThreadName("AccManager_ServerCallThread")  # FIXME: using protected apis
            env = {'User-Agent': bs.getEnvironment()['userAgentString']}
            if self._requestType != "get" or self._data:
                if self._requestType == 'get':
                    if self._data:
                        request = urllib2.Request(self._request + '?' + urllib.urlencode(self._data), None, env)
                    else:
                        request = urllib2.Request(self._request, None, env)
                elif self._requestType == 'post':
                    request = urllib2.Request(self._request, json.dumps(self._data), env)
                else:
                    raise RuntimeError("Invalid requestType: " + self._requestType)
                response = urllib2.urlopen(request)
            else:
                response = urllib2.urlopen(self._request)

            if self._eval_data:
                responseData = json.loads(response.read())
            else:
                responseData = response.read()
            if self._callback is not None:
                bs.callInGameThread(bs.Call(self._runCallback, responseData, response.getcode()))

        except:
            bs.printException()
            if self._callback is not None:
                bs.callInGameThread(bs.Call(self._runCallback, None, None))


def acc_serverGet(request, data, callback=None, eval_data=True):
    AccManager_ServerCallThread(request, 'get', data, callback, eval_data=eval_data).start()


def acc_serverPost(request, data, callback=None, eval_data=True):
    AccManager_ServerCallThread(request, 'post', data, callback, eval_data=eval_data).start()


class AccManagerWindow(Window):
    _selectedFile, _selectedFileIndex = None, None
    _selectedCont, _selectedContIndex = None, None
    _acc_tabs = set(["all"])
    tabs = []
    tabheight = 35
    files = []
    _fileWidgets = []
    contributors = []
    _contributorWidgets = []
    currently_fetching = False
    timers = {}

    def __init__(self, transition='inRight', modal=False, showTab="all", onCloseCall=None, backLocationCls=None,
                 originWidget=None):

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'

        self._backLocationCls = backLocationCls
        self._onCloseCall = onCloseCall
        self._showTab = showTab
        self._selectedTab = {'label': showTab}
        if showTab != "all":
            def check_tab_available():
                if not self._rootWidget.exists():
                    return
                if any([file.category == showTab for file in self.files]):
                    return
                if showTab == "contributors":
                    return
                if "button" in self._selectedTab:
                    return
                self._selectedTab = {"label": "all"}
                self._refresh()

            self.timers["check_tab_available"] = bs.Timer(300, check_tab_available, timeType='real')
        self._modal = modal

        self._windowTitleName = "Official Accessories Manager"

        def sort_rating(files):
            files = sorted(files, key=lambda file: file.rating_submissions, reverse=True)
            return sorted(files, key=lambda file: file.rating, reverse=True)

        def sort_downloads(files):
            return sorted(files, key=lambda file: file.downloads, reverse=True)

        def sort_alphabetical(files):
            return sorted(files, key=lambda file: file.name.lower())

        _sortModes = [
            ('Rating', sort_rating, lambda f: stats_cached()),
            ('Downloads', sort_downloads, lambda f: stats_cached()),
            ('Alphabetical', sort_alphabetical),
        ]

        self.sortModes = {}
        for i, sortMode in enumerate(_sortModes):
            name, func = sortMode[:2]
            next_sortMode = _sortModes[(i + 1) % len(_sortModes)]
            condition = sortMode[2] if len(sortMode) > 2 else (lambda mods: True)
            self.sortModes[name] = {
                'func': func,
                'condition': condition,
                'next': next_sortMode[0],
                'name': name,
                'index': i,
            }

        sortMode = config.get('sortMode')
        if not sortMode or sortMode not in self.sortModes:
            sortMode = _sortModes[0][0]
        self.sortMode = self.sortModes[sortMode]

        self._width = 650
        self._height = 380 if gSmallUI else 420 if gMedUI else 500
        topExtra = 20 if gSmallUI else 0

        self._rootWidget = ContainerWidget(size=(self._width, self._height + topExtra), transition=transition,
                                           scale=2.05 if gSmallUI else 1.5 if gMedUI else 1.0,
                                           stackOffset=(0, -10) if gSmallUI else (0, 0))

        self._backButton = backButton = ButtonWidget(parent=self._rootWidget,
                                                     position=(self._width - 160, self._height - 60),
                                                     size=(160, 68), scale=0.77,
                                                     autoSelect=True, textScale=1.3,
                                                     label=bs.Lstr(resource='doneText' if self._modal else 'backText'),
                                                     onActivateCall=self._back)
        self._rootWidget.cancelButton = backButton
        TextWidget(parent=self._rootWidget, position=(0, self._height - 47),
                   size=(self._width, 25),
                   text=self._windowTitleName, color=gHeadingColor,
                   maxWidth=290,
                   hAlign="center", vAlign="center")

        v = self._height - 59
        h = 41
        bColor = (0.6, 0.53, 0.63)
        bTextColor = (0.75, 0.7, 0.8)

        s = 1.1 if gSmallUI else 1.27 if gMedUI else 1.57
        v -= 63.0 * s
        self.refreshButton = ButtonWidget(parent=self._rootWidget,
                                          position=(h, v),
                                          size=(90, 58.0 * s),
                                          onActivateCall=bs.Call(self._cb_refresh, force_fresh=True),
                                          color=bColor,
                                          autoSelect=True,
                                          buttonType='square',
                                          textColor=bTextColor,
                                          textScale=0.7,
                                          label="Reload List")

        v -= 63.0 * s
        self.fileInfoButton = ButtonWidget(parent=self._rootWidget, position=(h, v), size=(90, 58.0 * s),
                                           onActivateCall=bs.Call(self._cb_info),
                                           color=bColor,
                                           autoSelect=True,
                                           textColor=bTextColor,
                                           buttonType='square',
                                           textScale=0.7,
                                           label="Accessory Info")

        v -= 63.0 * s
        self.sortButtonData = {"s": s, "h": h, "v": v, "bColor": bColor, "bTextColor": bTextColor}
        self.sortButton = ButtonWidget(parent=self._rootWidget, position=(h, v), size=(90, 58.0 * s),
                                       onActivateCall=bs.Call(self._cb_sorting),
                                       color=bColor,
                                       autoSelect=True,
                                       textColor=bTextColor,
                                       buttonType='square',
                                       textScale=0.7,
                                       label="Sorting:\n" + self.sortMode['name'])

        v -= 63.0 * s
        self.settingsButton = ButtonWidget(parent=self._rootWidget, position=(h, v), size=(90, 58.0 * s),
                                           onActivateCall=bs.Call(self._cb_settings),
                                           color=bColor,
                                           autoSelect=True,
                                           textColor=bTextColor,
                                           buttonType='square',
                                           textScale=0.7,
                                           label="Settings")

        v = self._height - 75
        self.columnPosY = self._height - 75 - self.tabheight
        self._scrollHeight = self._height - 119 - self.tabheight
        scrollWidget = ScrollWidget(parent=self._rootWidget, position=(140, self.columnPosY - self._scrollHeight),
                                    size=(self._width - 180, self._scrollHeight + 10))
        backButton.set(downWidget=scrollWidget, leftWidget=scrollWidget)
        self._columnWidget = ColumnWidget(parent=scrollWidget)

        for b in [self.refreshButton, self.fileInfoButton, self.settingsButton]:
            b.rightWidget = scrollWidget
        scrollWidget.leftWidget = self.refreshButton

        self._cb_refresh()

        backButton.onActivateCall = self._back
        self._rootWidget.startButton = backButton
        self._rootWidget.onCancelCall = backButton.activate
        self._rootWidget.selectedChild = scrollWidget

    def _refresh(self, refreshTabs=True):
        while len(self._fileWidgets) > 0:
            self._fileWidgets.pop().delete()
        while len(self._contributorWidgets) > 0:
            self._contributorWidgets.pop().delete()

        self._acc_tabs.add("characters")
        self._acc_tabs.add("maps")
        self._acc_tabs.add("contributors")
        if refreshTabs:
            self._refreshTabs()

        if self._selectedTab["label"] != "contributors":
            bs.Widget(edit=self.fileInfoButton, label=bs.Lstr(value="Accessory Info"))

            while not self.sortMode['condition'](self.files):
                self.sortMode = self.sortModes[self.sortMode['next']]
                self.sortButton.label = "Sorting:\n" + self.sortMode['name']

            self.files = self.sortMode["func"](self.files)
            visible = self.files[:]
            if self._selectedTab["label"] != "all":
                visible = [m for m in visible if m.category == self._selectedTab["label"][:-1]]

            for index, file in enumerate(visible):
                color = (0.6, 0.6, 0.7, 1.0)
                if file.is_installed():
                    color = (0.85, 0.85, 0.85, 1)
                    if file.checkUpdate():
                        if file.is_outdated():
                            color = (0.85, 0.3, 0.3, 1)
                        else:
                            color = (1, 0.84, 0, 1)

                w = TextWidget(parent=self._columnWidget, size=(self._width - 40, 24),
                               maxWidth=self._width - 110,
                               text=file.name,
                               hAlign='left', vAlign='center',
                               color=color,
                               alwaysHighlight=True,
                               onSelectCall=bs.Call(self._cb_select_file, index, file),
                               onActivateCall=bs.Call(self._cb_info, True),
                               selectable=True)
                w.showBufferTop = 50
                w.showBufferBottom = 50
                # hitting up from top widget shoud jump to 'back;
                if index == 0:
                    tab_button = self.tabs[int((len(self.tabs) - 1) / 2)]["button"]
                    w.upWidget = tab_button

                if self._selectedFile and file.filename == self._selectedFile.filename:
                    self._columnWidget.set(selectedChild=w, visibleChild=w)

                self._fileWidgets.append(w)
        else:
            bs.Widget(edit=self.fileInfoButton, label=bs.Lstr(value="Contributor Info"))

            visible = self.contributors[:]
            for index, contributor in enumerate(visible):
                color = (0.6, 0.6, 0.7, 1.0)

                w = TextWidget(parent=self._columnWidget, size=(self._width - 40, 24),
                               maxWidth=self._width - 110,
                               text=contributor.name,
                               hAlign='left', vAlign='center',
                               color=color,
                               alwaysHighlight=True,
                               onSelectCall=bs.Call(self._cb_select_cont, index, contributor),
                               onActivateCall=bs.Call(self._cb_info, True),
                               selectable=True)
                w.showBufferTop = 50
                w.showBufferBottom = 50
                # hitting up from top widget shoud jump to 'back;
                if index == 0:
                    tab_button = self.tabs[int((len(self.tabs) - 1) / 2)]["button"]
                    w.upWidget = tab_button

                if self._selectedCont and contributor.name == self._selectedCont.name:
                    self._columnWidget.set(selectedChild=w, visibleChild=w)

                self._contributorWidgets.append(w)

    def _refreshTabs(self):
        if not self._rootWidget.exists():
            return
        for t in self.tabs:
            for widget in t.values():
                if isinstance(widget, bs.Widget) or isinstance(widget, Widget):
                    widget.delete()
        self.tabs = []
        total = len(self._acc_tabs)
        columnWidth = self._width - 180
        tabWidth = 100
        tabSpacing = 12
        # _______/-characters-\_/-maps-\_/-contributors-\______
        for i, tab in enumerate(sorted(list(self._acc_tabs))):
            px = 140 + columnWidth / 2 - tabWidth * total / 2 + tabWidth * i
            pos = (px, self.columnPosY + 5)
            size = (tabWidth - tabSpacing, self.tabheight + 10)
            rad = 10
            center = (pos[0] + 0.1 * size[0], pos[1] + 0.9 * size[1])
            txt = TextWidget(parent=self._rootWidget, position=center, size=(0, 0),
                             hAlign='center', vAlign='center',
                             maxWidth=1.4 * rad, scale=0.6, shadow=1.0, flatness=1.0)
            button = ButtonWidget(parent=self._rootWidget, position=pos, autoSelect=True,
                                  buttonType='tab', size=size, label=tab, enableSound=False,
                                  onActivateCall=bs.Call(self._cb_select_tab, i),
                                  color=(0.52, 0.48, 0.63), textColor=(0.65, 0.6, 0.7))
            self.tabs.append({'text': txt,
                              'button': button,
                              'label': tab})

        for i, tab in enumerate(self.tabs):
            if self._selectedTab["label"] == tab["label"]:
                self._cb_select_tab(i, refresh=False)

    def _cb_select_tab(self, index, refresh=True):
        bs.playSound(bs.getSound('click01'))
        self._selectedTab = self.tabs[index]

        for i, tab in enumerate(self.tabs):
            button = tab["button"]
            if i == index:
                button.set(color=(0.5, 0.4, 0.93), textColor=(0.85, 0.75, 0.95))  # lit
            else:
                button.set(color=(0.52, 0.48, 0.63), textColor=(0.65, 0.6, 0.7))  # unlit
        if self._selectedTab["label"] == "contributors":
            bs.Widget(edit=self.fileInfoButton, label=bs.Lstr(value="Contributor Info"))
        else:
            bs.Widget(edit=self.fileInfoButton, label=bs.Lstr(value="Accessory Info"))
        if refresh:
            self._refresh(refreshTabs=False)

    def _cb_select_file(self, index, file):
        self._selectedFileIndex = index
        self._selectedFile = file

    def _cb_select_cont(self, index, contributor):
        self._selectedContIndex = index
        self._selectedCont = contributor

    def _cb_refresh(self, force_fresh=False):
        self.files = []

        self._refresh()
        self.currently_fetching = True

        def f(*args, **kwargs):
            kwargs["force_fresh"] = force_fresh
            self._cb_serverdata(*args, **kwargs)

        get_index(f, force_fresh=force_fresh)
        self.timers["showFetchingIndicator"] = bs.Timer(500, bs.WeakCall(self._showFetchingIndicator), timeType='real')

    def _cb_serverdata(self, data, status_code, force_fresh=False):
        if not self._rootWidget.exists():
            return
        self.currently_fetching = False
        if data:
            f, c, v = process_server_data(data)
            # when we got network add the network files
            netFiles = [File(d) for d in f.values()]
            self.files = netFiles
            netFilenames = [m.filename for m in netFiles]
            for file in self.files:
                file._files = {m.base: m for m in self.files}
            contributors = [Contributor(d) for d in c.values()]
            self.contributors = contributors
            self._refresh()
        else:
            bs.screenMessage('network error :(')
        fetch_stats(self._cb_stats, force_fresh=force_fresh)

    def _cb_stats(self, data, status_code):
        if not self._rootWidget.exists() or not data:
            return

        def fill_files_with(d, attr):
            for file_id, value in d.items():
                for file in self.files:
                    if file.base == file_id:
                        setattr(file, attr, value)

        fill_files_with(data.get('average_ratings', {}), 'rating')
        fill_files_with(data.get('own_ratings', {}), 'own_rating')
        fill_files_with(data.get('amount_ratings', {}), 'rating_submissions')
        fill_files_with(data.get('downloads', {}), 'downloads')

        self._refresh()

    def _showFetchingIndicator(self):
        if self.currently_fetching:
            bs.screenMessage("loading...")

    def _cb_info(self, withSound=False):
        if withSound:
            bs.playSound(bs.getSound('swish'))
        if self._selectedTab["label"] == "contributors":
            ContInfoWindow(self._selectedCont, self, originWidget=self.fileInfoButton)
        else:
            FileInfoWindow(self._selectedFile, self, originWidget=self.fileInfoButton)

    def _cb_settings(self):
        SettingsWindow(self._selectedFile, self, originWidget=self.settingsButton)

    def _cb_sorting(self):
        self.sortMode = self.sortModes[self.sortMode['next']]
        while not self.sortMode['condition'](self.files):
            self.sortMode = self.sortModes[self.sortMode['next']]
        config['sortMode'] = self.sortMode['name']
        bs.writeConfig()
        self.sortButton.label = "Sorting:\n" + self.sortMode['name']
        self._cb_refresh()

    def _back(self):
        self._rootWidget.doTransition(self._transitionOut)
        if not self._modal:
            uiGlobals['mainMenuWindow'] = self._backLocationCls(transition='inLeft').getRootWidget()
        if self._onCloseCall is not None:
            self._onCloseCall()


class UpdateFileWindow(Window):

    def __init__(self, file, onok, swish=True, back=False):
        self._back = back
        self.file = file
        self.onok = bs.WeakCall(onok)
        if swish:
            bs.playSound(bs.getSound('swish'))
        text = "Do you want to update %s?" if file.is_installed() else "Do you want to install %s?"
        text = text % (file.name)
        if file.changelog and file.is_installed():
            text += "\n\nChangelog:"
            for change in file.changelog:
                text += "\n" + change
        height = 100 * (1 + len(file.changelog) * 0.3) if file.is_installed() else 100
        width = 360 * (1 + len(file.changelog) * 0.15) if file.is_installed() else 360
        self._rootWidget = ConfirmWindow(text, self.ok, height=height, width=width).getRootWidget()

    def ok(self):
        self.file.install(lambda file, success: self.onok())


class DeleteFileWindow(Window):

    def __init__(self, file, onok, swish=True, back=False):
        self._back = back
        self.file = file
        self.onok = bs.WeakCall(onok)
        if swish:
            bs.playSound(bs.getSound('swish'))

        self._rootWidget = ConfirmWindow("Are you sure you want to delete " + file.name, self.ok).getRootWidget()

    def ok(self):
        self.file.delete(self.onok)
        QuitToApplyWindow()


class RateFileWindow(Window):
    levels = ["Poor", "Below Average", "Average", "Above Average", "Excellent"]
    icons = ["trophy0b", "trophy1", "trophy2", "trophy3", "trophy4"]

    def __init__(self, file, onok, swish=True, back=False):
        self._back = back
        self.file = file
        self.onok = onok
        if swish:
            bs.playSound(bs.getSound('swish'))
        text = "How do you want to rate {}?".format(file.name)

        okText = bs.Lstr(resource='okText')
        cancelText = bs.Lstr(resource='cancelText')
        width = 360
        height = 330

        self._rootWidget = ContainerWidget(size=(width, height), transition='inRight',
                                           scale=2.1 if gSmallUI else 1.5 if gMedUI else 1.0)

        TextWidget(parent=self._rootWidget, position=(width * 0.5, height - 30), size=(0, 0),
                   hAlign="center", vAlign="center", text=text, maxWidth=width * 0.9, maxHeight=height - 75)

        b = ButtonWidget(parent=self._rootWidget, autoSelect=True, position=(20, 20), size=(150, 50), label=cancelText,
                         onActivateCall=self._cancel)
        self._rootWidget.set(cancelButton=b)
        okButtonH = width - 175

        b = ButtonWidget(parent=self._rootWidget, autoSelect=True, position=(okButtonH, 20), size=(150, 50),
                         label=okText, onActivateCall=self._ok)

        self._rootWidget.set(selectedChild=b, startButton=b)

        columnPosY = height - 75
        _scrollHeight = height - 150

        scrollWidget = ScrollWidget(parent=self._rootWidget, position=(20, columnPosY - _scrollHeight),
                                    size=(width - 40, _scrollHeight + 10))
        columnWidget = ColumnWidget(parent=scrollWidget)

        self._rootWidget.set(selectedChild=columnWidget)

        self.selected = self.file.own_rating or 2
        for num, name in enumerate(self.levels):
            s = bs.getSpecialChar(self.icons[num]) + name
            w = TextWidget(parent=columnWidget, size=(width - 40, 24 + 8),
                           maxWidth=width - 110,
                           text=s,
                           scale=0.85,
                           hAlign='left', vAlign='center',
                           alwaysHighlight=True,
                           onSelectCall=bs.Call(self._select, num),
                           onActivateCall=bs.Call(self._ok),
                           selectable=True)
            w.showBufferTop = 50
            w.showBufferBottom = 50

            if num == self.selected:
                columnWidget.set(selectedChild=w, visibleChild=w)
                self._rootWidget.set(selectedChild=w)
            elif num == 4:
                w.downWidget = b

    def _select(self, index):
        self.selected = index

    def _cancel(self):
        self._rootWidget.doTransition('outRight')

    def _ok(self):
        if not self._rootWidget.exists():
            return
        self._rootWidget.doTransition('outLeft')
        self.onok(self.selected)


class QuitToApplyWindow(Window):

    def __init__(self):
        global quittoapply
        if quittoapply is not None:
            quittoapply.delete()
            quittoapply = None
        bs.playSound(bs.getSound('swish'))
        text = "Quit BS to load update?"
        if bs.getEnvironment()["platform"] == "android":
            text += "\n(On Android you have to close the activity)"
        self._rootWidget = quittoapply = ConfirmWindow(text, self._doFadeAndQuit).getRootWidget()

    def _doFadeAndQuit(self):
        # FIXME: using protected apis
        bsInternal._fadeScreen(False, time=200, endCall=bs.Call(bs.quit, soft=True))
        bsInternal._lockAllInput()
        # unlock and fade back in shortly.. just in case something goes wrong
        # (or on android where quit just backs out of our activity and we may come back)
        bs.realTimer(300, bsInternal._unlockAllInput)
        # bs.realTimer(300, bs.Call(bsInternal._fadeScreen,True))


class RedownloadAccInstaller(Window):

    def __init__(self):
        bs.playSound(bs.getSound('swish'))
        self._rootWidget = ConfirmWindow("The Accessories Manager requires a serious update, update \n" +
                                         "it and reload the BombSquad game if you want to use it, \n" +
                                         "else it may not work.",
                                         self._download).getRootWidget()

    def yes(self):

        def mod_url(data):
            if "commit_sha" in data and "filename" in data:
                commit_hexsha = data["commit_sha"]
                filename = data["filename"]
                yield "http://rawcdn.githack.com/{}/{}/utils/{}".format(USER_REPO, commit_hexsha, filename)
            if "url" in data:
                if SUPPORTS_HTTPS:
                    yield data["url"]
                url = str(data["url"]).replace("https", "http")
                bs.screenMessage(url)
                yield url

        installed = []
        installing = []

        def check_finished():
            if any([m not in installed for m in installing]):
                return
            bs.screenMessage("installed everything.")
            if os.path.isfile(modPath + __name__ + ".pyc"):
                os.remove(modPath + __name__ + ".pyc")
            if os.path.isfile(modPath + __name__ + ".py"):
                os.remove(modPath + __name__ + ".py")
                bs.screenMessage("deleted self")
            bs.screenMessage("activating accessories manager")
            __import__("accManager")

        def install(data, script):
            installing.append(script)
            bs.screenMessage("installing " + str(script))
            print("installing", script)
            for dep in data[script].get("requires", []):
                install(data, dep)
            filename = data[script]["filename"]

            def f(data):
                if not data:
                    bs.screenMessage("failed to download mod '{}'".format(filename))
                print("writing", filename)
                with open(modPath + filename, "wb") as f:
                    f.write(data)
                installed.append(script)
                check_finished()

            try_fetch_cb(mod_url(data[script]), f)

        def onIndex(data):
            if not data:
                bs.screenMessage("network error :(")
                return
            data = json.loads(data)
            install(data["utils"], "accManager")

        get_index(onIndex, branch=config.get("branch", "master"))

    def _download(self):
        # FIXME: using protected apis
        bsInternal._fadeScreen(False, time=200, endCall=bs.Call(self.yes, soft=True))
        bsInternal._lockAllInput()

        bs.realTimer(300, bsInternal._unlockAllInput)
        bs.realTimer(300, bs.Call(bsInternal._fadeScreen, True))


class FileInfoWindow(Window):
    def __init__(self, file, accManagerWindow, originWidget=None):
        # TODO: cleanup
        self.accManagerWindow = accManagerWindow
        self.file = file
        s = 1.1 if gSmallUI else 1.27 if gMedUI else 1.57
        bColor = (0.6, 0.53, 0.63)
        bTextColor = (0.75, 0.7, 0.8)
        width = 360 * s
        height = 40 + 100 * s
        if file.author:
            height += 25
        if not file.isLocal:
            height += 50
        if file.rating is not None:
            height += 50
        if file.downloads:
            height += 50

        buttons = sum([(file.checkUpdate() or not file.is_installed()), file.is_installed(), file.is_installed(), True])

        color = (1, 1, 1)
        textScale = 0.7 * s

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = None
            scaleOrigin = None
            transition = 'inRight'

        self._rootWidget = ContainerWidget(size=(width, height), transition=transition,
                                           scale=2.1 if gSmallUI else 1.5 if gMedUI else 1.0,
                                           scaleOriginStackOffset=scaleOrigin)

        pos = height * 0.9
        labelspacing = height / (7.0 if (file.rating is None and not file.downloads) else 7.5)

        if file.tag:
            TextWidget(parent=self._rootWidget, position=(width * 0.49, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text=file.name, scale=textScale * 1.5,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            TextWidget(parent=self._rootWidget, position=(width * 0.51, pos - labelspacing * 0.1),
                       hAlign="left", vAlign="center", text=file.tag, scale=textScale * 0.9,
                       color=(1, 0.3, 0.3), big=True, size=(0, 0))
        else:
            TextWidget(parent=self._rootWidget, position=(width * 0.5, pos), size=(0, 0),
                       hAlign="center", vAlign="center", text=file.name, scale=textScale * 1.5,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)

        pos -= labelspacing

        if file.author:
            TextWidget(parent=self._rootWidget, position=(width * 0.5, pos), size=(0, 0),
                       hAlign="center", vAlign="center", text="by " + file.author, scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing
            status = "installed"
            if not file.is_installed():
                status = "not installed"
            TextWidget(parent=self._rootWidget, position=(width * 0.45, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text="Status:", scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            status = TextWidget(parent=self._rootWidget, position=(width * 0.55, pos), size=(0, 0),
                                hAlign="left", vAlign="center", text=status, scale=textScale,
                                color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing * 0.775

        if file.downloads:
            TextWidget(parent=self._rootWidget, position=(width * 0.45, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text="Downloads:", scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            TextWidget(parent=self._rootWidget, position=(width * 0.55, pos), size=(0, 0),
                       hAlign="left", vAlign="center", text=str(file.downloads), scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing * 0.775

        if file.rating is not None:
            TextWidget(parent=self._rootWidget, position=(width * 0.45, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text="Rating:", scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            rating_str = bs.getSpecialChar(RateFileWindow.icons[file.rating]) + RateFileWindow.levels[file.rating]
            TextWidget(parent=self._rootWidget, position=(width * 0.4725, pos), size=(0, 0),
                       hAlign="left", vAlign="center", text=rating_str, scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing * 0.775
            submissions = "({} {})".format(file.rating_submissions,
                                           "submission" if file.rating_submissions < 2 else "submissions")
            TextWidget(parent=self._rootWidget, position=(width * 0.4725, pos), size=(0, 0),
                       hAlign="left", vAlign="center", text=submissions, scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos += labelspacing * 0.3

        if not file.author:
            pos -= labelspacing

        if not (gSmallUI or gMedUI):
            pos -= labelspacing * 0.25

        pos -= labelspacing * 2.55

        self.button_index = -1

        def button_pos():
            self.button_index += 1
            d = {
                1: [0.5],
                2: [0.3, 0.7],
                3: [0.2, 0.45, 0.8],
                4: [0.17, 0.390, 0.61, 0.825],
            }
            x = width * d[buttons][self.button_index]
            y = pos
            sx, sy = button_size()
            x -= sx / 2
            y += sy / 2
            return x, y

        def button_size():
            sx = {1: 100, 2: 80, 3: 80, 4: 75}[buttons] * s
            sy = 40 * s
            return sx, sy

        def button_text_size():
            return {1: 0.8, 2: 1.0, 3: 1.2, 4: 1.2}[buttons]

        if file.checkUpdate() or not file.is_installed():
            text = "Download " + file.category
            if file.is_outdated():
                text = "Update " + file.category
            elif file.checkUpdate():
                text = "Reset " + file.category
            self.downloadButton = ButtonWidget(parent=self._rootWidget,
                                               position=button_pos(), size=button_size(),
                                               onActivateCall=bs.Call(self._download, ),
                                               color=bColor,
                                               autoSelect=True,
                                               textColor=bTextColor,
                                               buttonType='square',
                                               textScale=button_text_size(),
                                               label=text)

        if file.is_installed():
            self.deleteButton = ButtonWidget(parent=self._rootWidget,
                                             position=button_pos(), size=button_size(),
                                             onActivateCall=bs.Call(self._delete),
                                             color=bColor,
                                             autoSelect=True,
                                             textColor=bTextColor,
                                             buttonType='square',
                                             textScale=button_text_size(),
                                             label="Delete " + file.category)

            self.rateButton = ButtonWidget(parent=self._rootWidget,
                                           position=button_pos(), size=button_size(),
                                           onActivateCall=bs.Call(self._rate),
                                           color=bColor,
                                           autoSelect=True,
                                           textColor=bTextColor,
                                           buttonType='square',
                                           textScale=button_text_size(),
                                           label=(
                                                   "Rate " + file.category) if file.own_rating is None else "Change Rating")

        okButtonSize = button_size()
        okButtonPos = button_pos()
        okText = bs.Lstr(resource='okText')
        b = ButtonWidget(parent=self._rootWidget, autoSelect=True, position=okButtonPos, size=okButtonSize,
                         label=okText, onActivateCall=self._ok)

        self._rootWidget.onCancelCall = b.activate
        self._rootWidget.selectedChild = b
        self._rootWidget.startButton = b

    def _ok(self):
        self._rootWidget.doTransition('outLeft' if self._transitionOut is None else self._transitionOut)

    def _delete(self):
        DeleteFileWindow(self.file, self.accManagerWindow._cb_refresh)
        self._ok()

    def _download(self):
        UpdateFileWindow(self.file, self.accManagerWindow._cb_refresh)
        self._ok()

    def _rate(self):

        def submit_cb():
            self.accManagerWindow._cb_refresh(force_fresh=True)

        def cb(rating):
            submit_file_rating(self.file, rating, submit_cb)

        RateFileWindow(self.file, cb)
        self._ok()


class ContInfoWindow(Window):
    def __init__(self, contributor, accManagerWindow, originWidget=None):
        # TODO: cleanup
        self.accManagerWindow = accManagerWindow
        self.cont = contributor
        s = 1.1 if gSmallUI else 1.27 if gMedUI else 1.57
        bColor = (0.6, 0.53, 0.63)
        bTextColor = (0.75, 0.7, 0.8)
        width = 360 * s
        height = 40 + 100 * s + 160

        color = (1, 1, 1)
        textScale = 0.7 * s

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = None
            scaleOrigin = None
            transition = 'inRight'

        self._rootWidget = ContainerWidget(size=(width, height), transition=transition,
                                           scale=2.1 if gSmallUI else 1.5 if gMedUI else 1.0,
                                           scaleOriginStackOffset=scaleOrigin)

        pos = height * 0.9
        labelspacing = height / 7.5

        TextWidget(parent=self._rootWidget, position=(width * 0.5, pos), size=(0, 0),
                   hAlign="center", vAlign="center", text=contributor.name, scale=textScale * 1.5,
                   color=color, maxWidth=width * 0.9, maxHeight=height - 75)

        pos -= labelspacing

        if contributor.contributions:
            TextWidget(parent=self._rootWidget, position=(width * 0.5, pos), size=(0, 0),
                       hAlign="center", vAlign="center", text="Contributions:\n" + contributor.contributions,
                       scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing
        """if contributor.name:
            TextWidget(parent=self._rootWidget, position=(width * 0.45, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text="Contributor\'s name:", scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            TextWidget(parent=self._rootWidget, position=(width * 0.55, pos), size=(0, 0),
                       hAlign="left", vAlign="center", text=contributor.name, scale=textScale,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)"""
        pos -= labelspacing * 0.775

        if contributor.tag:
            TextWidget(parent=self._rootWidget, position=(width * 0.49, pos), size=(0, 0),
                       hAlign="right", vAlign="center", text="Role:", scale=textScale * 1.0,
                       color=color, maxWidth=width * 0.9, maxHeight=height - 75)
            pos -= labelspacing * 0.775
            TextWidget(parent=self._rootWidget, position=(width * 0.51, pos - labelspacing * 0.1),
                       hAlign="center", vAlign="center", text=contributor.tag, scale=textScale * 0.9,
                       color=(1, 0.3, 0.3), big=True, size=(0, 0))
            pos -= labelspacing * 0.772

        if not (gSmallUI or gMedUI):
            pos -= labelspacing * 0.25

        pos -= labelspacing * 2.55

        if contributor.url:
            self.urlButton = ButtonWidget(parent=self._rootWidget,
                                          position=(74.80000000000001, 53.33928571428571),
                                          size=(122, 44),
                                          onActivateCall=bs.Call(bs.openURL, contributor.url),
                                          color=bColor,
                                          autoSelect=True,
                                          textColor=bTextColor,
                                          buttonType='square',
                                          textScale=1,
                                          label=bs.Lstr(value="Go to contributor\'s webpage"))

        okButtonSize = (88, 44)
        okButtonPos = (233.2, 53.3)
        okText = bs.Lstr(resource='okText')
        b = ButtonWidget(parent=self._rootWidget, autoSelect=True, position=okButtonPos, size=okButtonSize,
                         label=okText, onActivateCall=self._ok)

        self._rootWidget.onCancelCall = b.activate
        self._rootWidget.selectedChild = b
        self._rootWidget.startButton = b

    def _ok(self):
        self._rootWidget.doTransition('outLeft' if self._transitionOut is None else self._transitionOut)


class SettingsWindow(Window):
    def __init__(self, file, accManagerWindow, originWidget=None):
        self.accManagerWindow = accManagerWindow
        self.file = file
        s = 1.1 if gSmallUI else 1.27 if gMedUI else 1.57
        bTextColor = (0.75, 0.7, 0.8)
        width = 380 * s
        height = 240 * s
        textScale = 0.7 * s

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = None
            scaleOrigin = None
            transition = 'inRight'

        self._rootWidget = ContainerWidget(size=(width, height), transition=transition,
                                           scale=2.1 if gSmallUI else 1.5 if gMedUI else 1.0,
                                           scaleOriginStackOffset=scaleOrigin)

        self._titleText = TextWidget(parent=self._rootWidget, position=(0, height - 52),
                                     size=(width, 30), text="AccManager Settings", color=(1.0, 1.0, 1.0),
                                     hAlign="center", vAlign="top", scale=1.5 * textScale)

        pos = height * 0.65
        TextWidget(parent=self._rootWidget, position=(width * 0.35, pos), size=(0, 40),
                   hAlign="right", vAlign="center",
                   text="Branch:", scale=textScale,
                   color=bTextColor, maxWidth=width * 0.9, maxHeight=(height - 75))
        self.branch = TextWidget(parent=self._rootWidget, position=(width * 0.4, pos),
                                 size=(width * 0.4, 40), text=config.get("branch", "master"),
                                 hAlign="left", vAlign="center",
                                 editable=True, padding=4,
                                 onReturnPressCall=self.setBranch)

        pos -= height * 0.125
        checkUpdatesValue = config.get("submit-download-statistics", True)
        self.downloadStats = CheckBoxWidget(parent=self._rootWidget, text="submit download statistics",
                                            position=(width * 0.2, pos), size=(170, 30),
                                            textColor=(0.8, 0.8, 0.8),
                                            value=checkUpdatesValue,
                                            onValueChangeCall=self.setDownloadStats)

        pos -= height * 0.125
        checkUpdatesValue = config.get("auto-check-updates", True)
        self.checkUpdates = CheckBoxWidget(parent=self._rootWidget, text="automatically check for updates",
                                           position=(width * 0.2, pos), size=(170, 30),
                                           textColor=(0.8, 0.8, 0.8),
                                           value=checkUpdatesValue,
                                           onValueChangeCall=self.setCheckUpdate)

        pos -= height * 0.125
        autoUpdatesValue = config.get("auto-update-old-files", True)
        self.autoUpdates = CheckBoxWidget(parent=self._rootWidget, text="auto-update outdated files",
                                          position=(width * 0.2, pos), size=(170, 30),
                                          textColor=(0.8, 0.8, 0.8),
                                          value=autoUpdatesValue,
                                          onValueChangeCall=self.setAutoUpdate)
        self.checkAutoUpdateState()

        okButtonSize = (150, 50)
        okButtonPos = (width * 0.5 - okButtonSize[0] / 2, 20)
        okText = bs.Lstr(resource='okText')
        okButton = ButtonWidget(parent=self._rootWidget, position=okButtonPos, size=okButtonSize, label=okText,
                                onActivateCall=self._ok)

        self._rootWidget.set(onCancelCall=okButton.activate, selectedChild=okButton, startButton=okButton)

    def _ok(self):
        if self.branch.text() != config.get("branch", "master"):
            self.setBranch()
        self._rootWidget.doTransition('outLeft' if self._transitionOut is None else self._transitionOut)

    def setBranch(self):
        branch = self.branch.text()
        if branch == '':
            branch = "master"
        bs.screenMessage("fetching branch '" + branch + "'")

        def cb(data, status_code):
            newBranch = branch
            if data:
                bs.screenMessage('ok')
            else:
                bs.screenMessage('failed to fetch branch')
                newBranch = "master"
            bs.screenMessage("set branch to " + newBranch)
            config["branch"] = newBranch
            bs.writeConfig()
            self.accManagerWindow._cb_refresh()

        get_index(cb, branch=branch)

    def setCheckUpdate(self, val):
        config["auto-check-updates"] = bool(val)
        bs.writeConfig()
        self.checkAutoUpdateState()

    def checkAutoUpdateState(self):
        if not self.checkUpdates.value:
            # FIXME: properly disable checkbox
            self.autoUpdates.set(value=False,
                                 color=(0.65, 0.65, 0.65),
                                 textColor=(0.65, 0.65, 0.65))
        else:
            # FIXME: match original color
            autoUpdatesValue = config.get("auto-update-old-files", True)
            self.autoUpdates.set(value=autoUpdatesValue,
                                 color=(0.475, 0.6, 0.2),
                                 textColor=(0.8, 0.8, 0.8))

    def setAutoUpdate(self, val):
        # FIXME: properly disable checkbox
        if not self.checkUpdates.value:
            bs.playSound(bs.getSound("error"))
            self.autoUpdates.value = False
            return
        config["auto-update-old-files"] = bool(val)
        bs.writeConfig()

    def setDownloadStats(self, val):
        config["submit-download-statistics"] = bool(val)
        bs.writeConfig()


class Contributor:
    name = None
    url = False
    tag = False
    contributions = []
    data = None

    def __init__(self, d):
        self.data = d
        if "Real full name" in d:
            self.name = d.get('Common name') + "(" + d.get('Real full name') + ")"
        else:
            self.name = d.get('Common name')
        self.contributions = d.get("contributions", [])
        self.url = d.get('url', False)
        self.tag = d.get('tag', False)


class File:
    name = False
    author = None
    filename = None
    base = None
    changelog = []
    url = False
    isLocal = False
    category = None
    rating = None
    rating_submissions = 0
    own_rating = None
    downloads = None
    tag = None
    data = None
    oldmd5s = []

    def __init__(self, d):
        self.data = d
        self.author = d.get('author')
        if 'filename' in d:
            self.filename = d['filename']
            iter = self.filename.split(".")
            self.base = ""
            count = 0
            for i in iter:
                count += 1
                if count <= len(iter) - 1:
                    self.base += str(i) + "."
                else:
                    self.base += str(i)
            del iter
            del count
            del i
        else:
            raise RuntimeError('file without filename')
        if 'name' in d:
            self.name = d['name']
        else:
            self.name = self.filename
        if 'md5' in d:
            self.md5 = d['md5']
        else:
            raise RuntimeError('file without md5')

        self.changelog = d.get('changelog', [])
        self.oldmd5s = d.get('oldmd5s', [])
        self.category = d.get('category', None)
        if "insImport" in d:
            self.insImport = d.get('insImport')
        else:
            raise RuntimeError('file without insImport')
        self.tag = d.get('tag', None)
        self.isCollection = d.get("isCollection", False)
        if self.isCollection:
            if "collectionFiles" in d:
                self.collectionFiles = d.get("collectionFiles")
            else:
                raise RuntimeError('collection without collectionFiles')

    def writeData(self, callback, install, data, status_code):
        path = modPath + self.filename

        if data:
            if self.is_installed():
                """rename the old file to be able to recover it if something goes wrong"""
                if self.isCollection:
                    pass
                    """for file in self.collectionFiles:
                        os.rename(modPath + file, modPath + file + ".bak")"""
                else:
                    os.rename(path, path + ".bak")

            print("writing " + self.filename)
            with open(path, 'wb') as f:
                f.write(data)
                f.close()
        else:
            bs.printException()
            bs.screenMessage("Failed to write file")
        if callback:
            callback(self, data is not None)
        if install:
            __import__(self.insImport)
            bs.screenMessage("Succesfully installed " + self.name)

        submit_download(self)

    def install(self, callback, install=True):
        if self.isCollection:
            self.writeCollectionData(callback, install)
        else:
            fetch_file(self.data, partial(self.writeData, callback, install))

    def writeCollectionData(self, callback, install):
        if "commit_sha" in self.data and "filename" in self.data:
            try:
                bs.screenMessage("This may take more time than usual due to many files and slow network,\n" +
                                 "but it will surely install succesfully.")
                commit_hexsha = self.data["commit_sha"]
                filename = self.data["filename"]
                """Re using the backup if generated last time while deleting the collection"""
                if os.path.exists(modPath + self.data["dirname"]):
                    for fileto in self.collectionFiles:
                        os.rename(modPath+fileto+".bak", modPath+fileto)
                else:
                    os.mkdir(modPath + self.data["dirname"])

                    def yieldi(toyield):
                        yield str(toyield)

                    for fileto in self.collectionFiles:
                        url = "http://rawcdn.githack.com/" + USER_REPO + "/" + commit_hexsha + "/all-files/" + filename + "/" + str(
                            fileto)
                        url = yieldi(url)
                        url = next(url).encode("ascii")
                        data = urllib2.urlopen(url).read()
                        with open(modPath + fileto, "wb") as f:
                            f.write(data)
                            f.close()
                if callback:
                    callback(self, self.data)
                if install:
                    __import__(self.insImport)
                    bs.screenMessage("Successfully installed " + self.name)

                submit_download(self)
            except:
                bs.printException()
                bs.screenMessage("Failed to write the files of " + self.name)

        else:
            raise RuntimeError("Invalid accessory, " + self.name)

    @property
    def ownData(self):
        if self.isCollection:
            g = []
            for fileto in self.collectionFiles:
                path = modPath + fileto
                if os.path.exists(path):
                    with open(path, "r") as ownFile:
                        g.append(ownFile.read())
            return g
        else:
            path = modPath + self.insImport + ".py"
            if os.path.exists(path):
                with open(path, "r") as ownFile:
                    return ownFile.read()

    def delete(self, cb=None):
        path = modPath + self.filename
        """making backup for recovery"""
        if self.isCollection:
            for fileto in self.collectionFiles:
                os.rename(modPath + fileto, modPath + fileto + ".bak")
                if os.path.exists(modPath + fileto + "c"):  # check for python bytecode
                    os.remove(
                        modPath + fileto + "c")  # remove python bytecode because importing still works without .py file
        else:
            os.rename(path, path + ".bak")
        if os.path.exists(path + "c"):  # check for python bytecode
            os.remove(path + "c")  # remove python bytecode because importing still works without .py file
        if cb:
            cb()

    def checkUpdate(self):
        if not self.is_installed():
            return False
        if self.local_md5() != self.md5:
            return True
        return False

    def up_to_date(self):
        return self.is_installed() and self.local_md5() == self.md5

    def is_installed(self):
        if os.path.exists(modPath + self.insImport + ".py"):
            return True
        return False

    def local_md5(self):
        if self.isCollection:
            g = ""
            for data in self.ownData:
                g += md5(data).hexdigest()
            return g
        else:
            return md5(self.ownData).hexdigest()

    def is_outdated(self):
        if not self.is_installed():
            return False
        local_md5 = self.local_md5()
        if local_md5 in self.oldmd5s:
            return True
        return False
