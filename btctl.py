import sys
import re
import subprocess


class BluetoothCtl:

    def __init__(self, deviceMacs, executable="bluetoothctl"):
        self.exec = executable
        self.deviceMacs = deviceMacs

    def execCommand(self, cmd):
        p = subprocess.Popen(
            [self.exec]+cmd, stdout=subprocess.PIPE, text=True)
        p.wait()
        return ExecData(p.stdout.readlines(), p.returncode)

    def pair(self, mac):
        response = self.execCommand(["pair", mac])
        return response.succeeded()

    def trust(self):
        response = self.execCommand(["trust", mac])
        return response.succeeded()

    def connect(self):
        response = self.execCommand(["connect", mac])
        return response.succeeded()

    def disconnect(self):
        response = self.execCommand(["disconnect", mac])
        return response.succeeded()

    def info(self, mac):
        response = self.execCommand(["info", mac])
        if not response.succeeded():
            return None
        return BluetoothCtlInfo(response.output)

    def isConnected(self, deviceMac=None):
        if deviceMac is not None:
            return self.info(deviceMac).isConnected()
        else:
            for macs in self.deviceMacs:
                c = self.info(macs).isConnected()
                if not c:
                    return False
            return True


class BluetoothCtlInfo:

    regexName = r"Name:[\ ]*(.*)\n"
    regexPaired = r"Paired:[\ ]*(.*)\n"
    regexTrusted = r"Trusted:[\ ]*(.*)\n"
    regexConnected = r"Connected:[\ ]*(.*)\n"

    def __init__(self, response):
        matches = re.findall(self.regexName, response)
        self.name = matches[0]
        matches = re.findall(self.regexPaired, response)
        self.paired = matches[0] == "yes"
        matches = re.findall(self.regexTrusted, response)
        self.trusted = matches[0] == "yes"
        matches = re.findall(self.regexConnected, response)
        self.connected = matches[0] == "yes"

    def getName(self):
        return self.name

    def isPaired(self):
        return self.paired

    def isTrusted(self):
        return self.trusted

    def isConnected(self):
        return self.connected

    def __str__(self):
        return "BluetoothCtlInfo[ Name="+self.name+" Paired="+str(self.paired)+" Trusted="+str(self.trusted)+" Connected="+str(self.trusted)+"]"


class ExecData:

    def __init__(self, output, code):
        self.returnCode = code
        if type(output) is list:
            output = ' '.join(output)
        self.output = output

    def succeeded(self):
        return self.returnCode == 0

    def __str__(self):
        return "ExecData [returnCode="+str(self.returnCode)+" output="+str(self.output)+"]"
