import bs
import bsInternal
import threading
import json
import urllib2
import weakref
import os
import os.path

import httplib
SUPPORTS_HTTPS = hasattr(httplib, 'HTTPS')

modPath = bs.getEnvironment()['userScriptsDirectory'] + "/"
BRANCH = "master"
USER_REPO = "I-Am-The-Great/BombSquad-Official-Accessory-Archive"
ENTRY_MOD = "accManager"


def index_url():
    if SUPPORTS_HTTPS:
        yield "https://raw.githubusercontent.com/{}/{}/index.json".format(USER_REPO, BRANCH)
    yield "http://raw.githack.com/{}/{}/index.json".format(USER_REPO, BRANCH)


def mod_url(data):
    if "commit_sha" in data and "filename" in data:
        commit_hexsha = data["commit_sha"]
        filename = data["filename"]
        yield "http://rawcdn.githack.com/{}/{}/utils/{}".format(USER_REPO, commit_hexsha, filename)
    if "url" in data:
        if SUPPORTS_HTTPS:
            yield data["url"]
        url = str(data["url"]).replace("https", "http")
        yield url


def try_fetch_cb(generator, callback):
    def f(data):
        if data:
            callback(data)
        else:
            try:
                SimpleGetThread(next(generator), f).start()
            except StopIteration:
                callback(None)
    SimpleGetThread(next(generator), f).start()


class SimpleGetThread(threading.Thread):
    def __init__(self, url, callback=None):
        threading.Thread.__init__(self)
        if SUPPORTS_HTTPS:
            url = url
        else:
            url = url.replace("https", "http")
        self._url = url.encode("ascii")  # embedded python2.7 has weird encoding issues
        self._callback = callback or (lambda d: None)
        self._context = bs.Context('current')
        # save and restore the context we were created from
        activity = bs.getActivity(exceptionOnNone=False)
        self._activity = weakref.ref(activity) if activity is not None else None

    def _runCallback(self, arg):
        # if we were created in an activity context and that activity has since died, do nothing
        # (hmm should we be using a context-call instead of doing this manually?)
        if self._activity is not None and (self._activity() is None or self._activity().isFinalized()):
            return
        # (technically we could do the same check for session contexts, but not gonna worry about it for now)
        with self._context:
            self._callback(arg)

    def run(self):
        try:
            bsInternal._setThreadName("SimpleGetThread")
            response = urllib2.urlopen(self._url)
            bs.callInGameThread(bs.Call(self._runCallback, response.read()))
        except Exception:
            bs.printException()
            bs.callInGameThread(bs.Call(self._runCallback, None))


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
    __import__(ENTRY_MOD)


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
    install(data["utils"], ENTRY_MOD)



try_fetch_cb(index_url(), onIndex)
