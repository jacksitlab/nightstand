import sys
import json
from config.key import KeyConfig


def testKeyConfig():
    cfg1 = KeyConfig(json.loads('{"color":"#FFFFFF"}'))
    print("config1=", cfg1)
    cfg2 = KeyConfig(json.loads('{"color":"#000000"}'))
    print("config1=", cfg2)
    cfg3 = KeyConfig(json.loads('{"color":"#FF0000"}'))
    print("config1=", cfg3)
    cfg4 = KeyConfig(json.loads('{"color":"#00FF00"}'))
    print("config1=", cfg4)
    cfg5 = KeyConfig(json.loads('{"color":"#0000FF"}'))
    print("config1=", cfg5)
    cfg6 = KeyConfig(json.loads('{"color":"#0F0F0F"}'))
    print("config1=", cfg6)


if __name__ == '__main__':
    testKeyConfig()
