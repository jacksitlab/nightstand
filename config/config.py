import json
from datetime import datetime, timedelta
from .key import KeyConfig
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NightStandConfig(FileSystemEventHandler):

    def __init__(self, filename):
        self.filename = filename
        self.last_modified = datetime.now()
        self.changeListeners = []
        eventhandler = self
        self.fileObserver = Observer()
        self.fileObserver.schedule(
            self, path='./', recursive=False)
        self.fileObserver.start()

    def load(self):
        with open(self.filename) as json_data:
            self.data = json.load(json_data)

    def on_modified(self, event):
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        print(f'event type: {event.event_type}  path : {event.src_path}')
        if str(event.src_path).endswith(self.filename):
            self.onConfigChanged()

    def onConfigChanged(self):
        print("config has changed")
        try:
            self.load()
        except:
            print("error reloading config")
            return

        for listener in self.changeListeners:
            listener()

    def registerFilechangedListener(self, listener):
        self.changeListeners.append(listener)

    def unregisterFileChangedListener(self, listener):
        self.changeListeners.remove(listener)

    def join(self):
        self.fileObserver.join()

    def stop(self):
        self.fileObserver.stop()

    def getKeyConfig(self, index):
        keys = self.data["keys"]
        if str(index) in keys:
            return KeyConfig(keys[str(index)])
        else:
            return KeyConfig.Default()

    def getMedia(self, index):
        keyconfig = self.getKeyConfig(index)
        media = self.data["media"]
        if keyconfig.mediaId in media:
            return media[keyconfig.mediaId]
        return None

    def isSleepEnabled(self):
        sleep = self.data["sleep"]
        return sleep["enabled"]

    def getSleepTime(self):
        sleep = self.data["sleep"]
        return sleep["timer"]
