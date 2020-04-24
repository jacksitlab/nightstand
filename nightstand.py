import sys
import time
from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from config.config import NightStandConfig

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

CONFIGFILE = "config.json"


class Nightstand:

    def __init__(self):
        self.config = NightStandConfig(CONFIGFILE)

    def init(self):
        self.config.load()
        self.config.registerFilechangedListener(self.onConfigChanged)
        # create the i2c object for the trellis
        i2c_bus = busio.I2C(SCL, SDA)
        # create the trellis
        self.trellis = NeoTrellis(i2c_bus)
        for i in range(16):
            # activate rising edge events on all keys
            self.trellis.activate_key(i, NeoTrellis.EDGE_RISING)
            # activate falling edge events on all keys
            self.trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
            # set all keys to trigger the blink callback
            self.trellis.callbacks[i] = self.onKeyPressed

    def reset(self, startupSequence = True):
        if startupSequence:
            for i in range(16):
                self.trellis.pixels[i] = RED
                time.sleep(0.1)
            for i in range(16):
                self.trellis.pixels[i] = YELLOW
                time.sleep(0.1)
            for i in range(16):
                self.trellis.pixels[i] = GREEN
                time.sleep(0.1)
            for i in range(16):
                self.trellis.pixels[i] = OFF
                time.sleep(0.1)
        for i in range(16):
            self.trellis.pixels[i] = self.config.getKeyConfig(i).color
            time.sleep(0.1)

    def onConfigChanged(self):
        print("config changed")
        self.reset(False)

    def onKeyPressed(self, event):
        # turn the LED on when a rising edge is detected
        if event.edge == NeoTrellis.EDGE_RISING:
            self.trellis.pixels[event.number] = self.config.getKeyConfig(
                event.number).keyPressedColor
        # turn the LED off when a rising edge is detected
        elif event.edge == NeoTrellis.EDGE_FALLING:
            self.trellis.pixels[event.number] = self.config.getKeyConfig(
                event.number).color

    def startServer(self):
        print('Hello from the Nightstand Service')
        while True:
            # call the sync function call any triggered callbacks
            self.trellis.sync()
            # the trellis can only be read every 17 millisecons or so
            time.sleep(0.02)

    def startCLI(self):
        print('Hello from the Nightstand Server')
        self.reset()
        try:
            while True:
                # call the sync function call any triggered callbacks
                self.trellis.sync()
                # the trellis can only be read every 17 millisecons or so
                time.sleep(0.02)
        except KeyboardInterrupt:
            self.config.stop()
        self.config.join()


if __name__ == '__main__':
    import time
    import systemd.daemon

    ds = Nightstand()
    print('Starting up ...')
    ds.init()
    print('Startup complete')
    if len(sys.argv) <= 1:
        ds.startServer()
    else:
        ds.startCLI()

    # Tell systemd that our service is ready
#    systemd.daemon.notify('READY=1')
