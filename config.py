import json


class NightStandConfig:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        with open(self.filename) as json_data:
            self.data = json.load(json_data)

    def registerFilechangedLister(self, listener):
        pass
