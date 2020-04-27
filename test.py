import sys
import json
from config.key import KeyConfig
from btctl import BluetoothCtlInfo, BluetoothCtl


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


def testBtCtlInfo():
    response = """Device 00:42:79:A7:6F:CE (public)
        Name: JBL Flip 4
        Alias: JBL Flip 4
        Class: 0x00240414
        Icon: audio-card
        Paired: no
        Trusted: yes
        Blocked: no
        Connected: no
        LegacyPairing: no
        UUID: Headset                   (00001108-0000-1000-8000-00805f9b34fb)
        UUID: Audio Sink                (0000110b-0000-1000-8000-00805f9b34fb)
        UUID: A/V Remote Control Target (0000110c-0000-1000-8000-00805f9b34fb)
        UUID: Advanced Audio Distribu.. (0000110d-0000-1000-8000-00805f9b34fb)
        UUID: A/V Remote Control        (0000110e-0000-1000-8000-00805f9b34fb)
        UUID: Handsfree                 (0000111e-0000-1000-8000-00805f9b34fb)
        UUID: PnP Information           (00001200-0000-1000-8000-00805f9b34fb)
        Modalias: bluetooth:v000ApFFFFdFFFF
        ManufacturerData Key: 0x0057
        ManufacturerData Value:
  d1 1e 01 00 d8 63                                 .....c """

    info = BluetoothCtlInfo(response)
    print("name="+info.getName())
    print("paired="+str(info.isPaired()))
    print("trusted="+str(info.isTrusted()))
    print("connected="+str(info.isConnected()))


def testBtConnection():
    mac = "00:42:79:A7:6F:CE"

    btctl = BluetoothCtl([mac])
    btctl.info(mac)


if __name__ == '__main__':
    testKeyConfig()
    testBtCtlInfo()
    testBtConnection()
