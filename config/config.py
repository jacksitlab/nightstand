import json
from .key import KeyConfig


class NightStandConfig:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        with open(self.filename) as json_data:
            self.data = json.load(json_data)

    def registerFilechangedLister(self, listener):
        pass

    def getKeyConfig(self, index):
        keys = self.data["keys"]
        if str(index) in keys:
            return KeyConfig(keys[str(index)])
        else:
            return KeyConfig.Default()
