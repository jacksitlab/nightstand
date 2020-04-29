import sys
import re
import subprocess
import time
import threading

DELAY = 5


class BluetoothCtl:

    def __init__(self, deviceMacs, executable="bluetoothctl"):
        self.exec = executable
        self.deviceMacs = deviceMacs
        self.cancelConnect = False
        self.connectIsRunning = False

    def doConnectAsync(self, retries, onSuccess, onFailed):
        threading.Thread(target=self.doConnect, args=(
            retries, onSuccess, onFailed))

    def doConnect(self, retries, onSuccess, onFailed):
        self.cancelConnect = False
        if self.isConnected():
            onSuccess()
            return
        self.connectIsRunning = True
        for i in range(retries):
            res = True
            for mac in self.deviceMacs:
                if self.cancelConnect:
                    break
                cr = self.connect(mac)
                res = res and cr
            if res:
                onSuccess()
                self.connectIsRunning = False
                return
            time.sleep(DELAY)

        onFailed()
        self.connectIsRunning = False

    def doDisconnect(self):
        if self.connectIsRunning:
            self.cancelConnect = True
            i = 4
            while self.connectIsRunning and i > 0:
                time.sleep(1)
                i -= 1
        self.disconnect()

    def execCommand(self, cmd):
        p = subprocess.Popen(
            [self.exec]+cmd, stdout=subprocess.PIPE, text=True)
        p.wait()
        return ExecData(p.stdout.readlines(), p.returncode)

    def pair(self, deviceMac=None):
        if deviceMac is not None:
            return self.execCommand(["pair", deviceMac]).succeeded()
        else:
            success = True
            for mac in self.deviceMacs:
                success = success and self.pair(mac)
            return success

    def trust(self, deviceMac=None):
        if deviceMac is not None:
            return self.execCommand(["trust", deviceMac]).succeeded()
        else:
            success = True
            for mac in self.deviceMacs:
                success = success and self.trust(mac)
            return success

    def connect(self, deviceMac=None):
        if deviceMac is not None:
            return self.execCommand(["connect", deviceMac]).succeeded()
        else:
            success = True
            for mac in self.deviceMacs:
                success = success and self.connect(mac)
            return success

    def disconnect(self, deviceMac=None):
        if deviceMac is not None:
            return self.execCommand(["disconnect", deviceMac]).succeeded()
        else:
            success = True
            for mac in self.deviceMacs:
                success = success and self.disconnect(mac)
            return success

    def info(self, deviceMac):
        response = self.execCommand(["info", deviceMac])
        if not response.succeeded():
            return None
        return BluetoothCtlInfo(response.output)

    def isConnected(self, deviceMac=None):
        if deviceMac is not None:
            return self.info(deviceMac).isConnected()
        else:
            for mac in self.deviceMacs:
                c = self.info(mac).isConnected()
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
