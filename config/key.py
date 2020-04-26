import sys
import json


class KeyConfig:

    AUDIOBUTTON_PLAY_PAUSE = "PLAY"
    AUDIOBUTTON_STOP = "STOP"
    AUDIOBUTTON_VOLUMEUP = "VOL+"
    AUDIOBUTTON_VOLUMEDOWN = "VOL-"
    AUDIOBUTTON_NEXT = "NEXT"
    AUDIOBUTTON_PREV = "PREV"

    def __init__(self, keydata):
        self.color = self.colorFromHexCode(keydata["color"])
        self.keyPressedColor = self.color
        if "pressed" in keydata:
            self.keyPressedColor = self.colorFromHexCode(keydata["pressed"])
        self.mediaId = ""
        if "media" in keydata:
            self.mediaId = keydata["media"]
        self.playerButton = None
        if "player" in keydata:
            self.playerButton = keydata["player"]

    def colorFromHexCode(self, hex):
        r = int(hex[1:3], 16)
        g = int(hex[3:5], 16)
        b = int(hex[5:], 16)
        return (r, g, b)

    def isPlayerButton(self):
        return self.playerButton != None

    def __str__(self):
        return "KeyConfig[ Color[r="+str(self.color[0])+" g="+str(self.color[1])+" b="+str(self.color[2])+"], ColorKeyPressed[r="+str(self.keyPressedColor[0])+" g="+str(self.keyPressedColor[1])+" b="+str(self.keyPressedColor[2])+"], mediaId="+self.mediaId+"]"

    @staticmethod
    def Default():
        return KeyConfig(json.loads('{"color":"#000000","pressed":"#FFFFFF","media":""}'))
