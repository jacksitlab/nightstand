import sys
import json


class KeyConfig:

    def __init__(self, keydata):
        self.color = self.colorFromHexCode(keydata["color"])
        self.keyPressedColor = self.colorFromHexCode(keydata["pressed"])

    def colorFromHexCode(self, hex):
        r = int(hex[1:3], 16)
        g = int(hex[3:5], 16)
        b = int(hex[5:], 16)
        return (r, g, b)

    def __str__(self):
        return "KeyConfig[ Color[r="+str(self.color[0])+" g="+str(self.color[1])+" b="+str(self.color[2])+"]]"

    @staticmethod
    def Default():
        return KeyConfig(json.loads('{"color":"#000000","pressed":"#FFFFFF"}'))
