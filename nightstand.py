import sys
import time
from board import SCL, SDA
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from config.config import NightStandConfig
from repeatedTimer import RepeatedTimer
from config.key import KeyConfig
import vlc

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)

CONFIGFILE = "config.json"
INIT_DELAY = 0.05
TIMER_INTERVAL = 2
TIME_TO_RESET = 10
TIME_TO_SLEEPMENU = 5
TIME_TO_SLEEPMENU_FALLBACK = 10
TIME_TO_DIMM = 60

RESET_COUNTER_START = TIME_TO_RESET/TIMER_INTERVAL
SLEEPMENU_COUNTER_START = TIME_TO_SLEEPMENU/TIMER_INTERVAL
SLEEPMENU_FALLBACK_COUNTER_START = TIME_TO_SLEEPMENU_FALLBACK/TIMER_INTERVAL
DIMMINGCOUNTER_START = TIME_TO_DIMM/TIMER_INTERVAL

MENUSTATE_INIT = 0
MENUSTATE_IDLE = 1
MENUSTATE_PLAYING = 2
MENUSTATE_SLEEPCONFIG = 3
MENUSTATE_SLEEPING = 4
MENUSTATE_DIMMING = 5

RESET_STATE_NONE = 0
RESET_STATE_KEYPRESSED = 1
KEYSTATE_NONE = 0
KEYSTATE_PRESSED = 1
# increase/decrease for VOL+/VOL- Button
VOL_INCDEC = 5


class NightstandStates:

    def __init__(self):
        self.menuStateOld = MENUSTATE_INIT
        self.menuState = MENUSTATE_INIT
        self.resetState = RESET_STATE_NONE
        self.resetCounter = RESET_COUNTER_START
        self.keyStates = [KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE,
                          KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE,
                          KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE,
                          KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE, KEYSTATE_NONE]
        self.sleepMenuCounter = SLEEPMENU_COUNTER_START
        self.sleepConfigFallbackCounter = SLEEPMENU_FALLBACK_COUNTER_START
        self.dimmingCounter = DIMMINGCOUNTER_START
        self.sleepEnabled = False
        self.menuStateChangeListeners = []
        self.resetListeners = []

    def enterMenu(self, state, force=False):
        if state == self.menuState and not force:
            return
        self.menuStateOld = self.menuState
        self.menuState = state
        for listener in self.menuStateChangeListeners:
            listener(self.menuStateOld, state)

    def menuBack(self):
        old = self.menuState
        self.menuState = self.menuStateOld
        for listener in self.menuStateChangeListeners:
            listener(self.menuStateOld, self.menuState)

    def isSleepCondition(self):
        if self.menuState == MENUSTATE_SLEEPING:
            return True
        self.sleepCounter -= 1
        if self.sleepEnabled and (self.menuState == MENUSTATE_IDLE or self.menuState == MENUSTATE_PLAYING) and self.sleepCounter < 0:
            return True
        return False

    def isSleepMenuKeyCondition(self):
        if self.keyStates[13] == KEYSTATE_PRESSED and self.keyStates[14] == KEYSTATE_PRESSED:
            return True
        return False

    def isResetKeyCondition(self):
        if self.keyStates[12] == KEYSTATE_PRESSED and self.keyStates[15] == KEYSTATE_PRESSED:
            return True
        return False

    def registerMenuStateChangeListener(self, listener):
        self.menuStateChangeListeners.append(listener)

    def unregisterMenuStateChangeListener(self, listener):
        self.menuStateChangeListeners.remove(listener)

    def registerResetListener(self, listener):
        self.resetListeners.append(listener)

    def unregisterResetListener(self, listener):
        self.resetListeners.remove(listener)

    def onResetTimerTick(self):
        if self.isResetKeyCondition():
            self.resetCounter -= 1
            if self.resetCounter < 0:
                self.pushReset()
        else:
            self.resetCounter = RESET_COUNTER_START

    def onSleepTimerTick(self):
        if self.menuState == MENUSTATE_SLEEPCONFIG:
            self.sleepConfigFallbackCounter -= 1
            if self.sleepConfigFallbackCounter < 0:
                self.menuBack()
        else:
            if self.isSleepMenuKeyCondition():
                self.sleepMenuCounter -= 1
                if self.sleepMenuCounter < 0:
                    self.enterMenu(MENUSTATE_SLEEPCONFIG)
            else:
                self.sleepMenuCounter = SLEEPMENU_COUNTER_START

    def onDimmingTimerTick(self):
        if self.dimmingCounter > 0:
            self.dimmingCounter -= 1
        if self.dimmingCounter <= 0:
            self.enterMenu(MENUSTATE_DIMMING)

    def pushReset(self):
        for listener in self.resetListeners:
            listener()

    def resetDimmingTimer(self):
        self.dimmingCounter = DIMMINGCOUNTER_START

    def stayinSleepConfig(self):
        self.sleepConfigFallbackCounter = SLEEPMENU_FALLBACK_COUNTER_START


class Nightstand:

    def __init__(self):
        self.config = NightStandConfig(CONFIGFILE)
        self.audioPlayer = None
        self.states = NightstandStates()
        self.states.registerMenuStateChangeListener(self.onMenuChanged)
        self.states.registerResetListener(self.reset)
        self.timer = RepeatedTimer(TIMER_INTERVAL, self.onTimerTick)

    def init(self):
        self.states.enterMenu(MENUSTATE_INIT)
        self.config.load()
        self.states.sleepEnabled = self.config.isSleepEnabled()
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
        self.states.enterMenu(MENUSTATE_IDLE)

    def onMenuChanged(self, oldMenuState, newMenuState):
        print("menu changed from "+str(oldMenuState) + " to " + str(newMenuState))
        if oldMenuState == MENUSTATE_SLEEPCONFIG:
            self.states.enterMenu(
                MENUSTATE_PLAYING if self.audioPlayer is not None else MENUSTATE_IDLE, True)
            return

        self.initColors()

    def reset(self, startupSequence=True, stopAudio=False):
        self.states.enterMenu(MENUSTATE_INIT)
        self.states.resetCounter = RESET_COUNTER_START
        if stopAudio:
            self.playAudio(None)
        if startupSequence:
            for i in range(16):
                self.trellis.pixels[i] = RED
                time.sleep(INIT_DELAY)
            for i in range(16):
                self.trellis.pixels[i] = YELLOW
                time.sleep(INIT_DELAY)
            for i in range(16):
                self.trellis.pixels[i] = GREEN
                time.sleep(INIT_DELAY)
            for i in range(16):
                self.trellis.pixels[i] = OFF
                time.sleep(INIT_DELAY)
        self.initColors()
        self.states.enterMenu(MENUSTATE_IDLE)

    def getKeyColor(self, index):
        if self.states.menuState == MENUSTATE_SLEEPCONFIG:
            time = self.config.getSleepTime()
            if index < 12:
                return YELLOW if time > index*300 else OFF
            elif index == 12:
                return WHITE
            elif index == 13:
                return GREEN if self.config.isSleepEnabled() else RED
            elif index == 14:
                return GREEN if self.config.isSleepEnabled() else RED
            elif index == 15:
                return WHITE
        elif self.states.menuState == MENUSTATE_DIMMING:
            return OFF
        else:
            kc = self.config.getKeyConfig(index)
            if not kc.isPlayerButton() or self.states.menuState == MENUSTATE_PLAYING:
                return kc.color
            else:
                return OFF

    def initColors(self):
        for i in range(16):
            self.trellis.pixels[i] = self.getKeyColor(i)

    def onTimerTick(self):
        self.states.onResetTimerTick()
        self.states.onSleepTimerTick()
        self.states.onDimmingTimerTick()

    def onConfigChanged(self):
        print("config changed")
        self.reset(False)

    def onKeyPressed(self, event):
        self.states.resetDimmingTimer()

        # turn the LED on when a rising edge is detected
        if event.edge == NeoTrellis.EDGE_RISING:
            self.trellis.pixels[event.number] = self.config.getKeyConfig(
                event.number).keyPressedColor
            self.states.keyStates[event.number] = KEYSTATE_PRESSED
        # turn the LED off when a rising edge is detected
        elif event.edge == NeoTrellis.EDGE_FALLING:
            if self.states.menuState == MENUSTATE_DIMMING:
                self.states.menuBack()
                return
            kc = self.config.getKeyConfig(event.number)
            if not kc.isPlayerButton() or self.states.menuState == MENUSTATE_PLAYING:
                self.trellis.pixels[event.number] = kc.color
            else:
                self.trellis.pixels[event.number] = OFF
            if self.states.menuState == MENUSTATE_SLEEPCONFIG:
                self.onSleepConfigKeyPressed(event.number)
            else:
                self.onAudioKeyPressed(event.number)
            self.states.keyStates[event.number] = KEYSTATE_NONE

    def onSleepConfigKeyPressed(self, index):
        curSleep = self.config.getSleepTime()
        incdec = 300
        if index == 12:
            self.config.setSleepTime(
                curSleep-incdec if curSleep > incdec else 0)
            if self.config.getSleepTime() == 0:
                self.config.enableSleep(False)
        if index == 15:
            self.config.setSleepTime(
                curSleep+incdec if curSleep < 11*incdec else 12*incdec)
            if curSleep == 0:
                self.config.enableSleep(True)
        if index == 13 or index == 14:
            self.config.enableSleep(not self.config.isSleepEnabled())
        self.states.stayinSleepConfig()
        self.initColors()

    def onAudioKeyPressed(self, index):
        if self.states.menuState == MENUSTATE_IDLE or (self.states.menuState == MENUSTATE_PLAYING and not self.config.getKeyConfig(index).isPlayerButton()):
            print("start audio")
            self.playAudio(self.config.getMedia(index))
        elif self.states.menuState == MENUSTATE_PLAYING:
            keyConfig = self.config.getKeyConfig(index)
            if keyConfig.isPlayerButton():
                self.audioPlayerButtonClick(keyConfig.playerButton)

    def audioPlayerButtonClick(self, button):
        print("exec audio button ", button)
        if not self.audioPlayer is None:
            if button == KeyConfig.AUDIOBUTTON_PLAY_PAUSE:
                if self.audioPlayer.is_playing():
                    self.audioPlayer.pause()
                else:
                    self.audioPlayer.play()
            elif button == KeyConfig.AUDIOBUTTON_STOP:
                self.playAudio(None)
            elif button == KeyConfig.AUDIOBUTTON_VOLUMEUP:
                vol = self.audioPlayer.audio_get_volume()+VOL_INCDEC
                self.audioPlayer.audio_set_volume(vol)
            elif button == KeyConfig.AUDIOBUTTON_VOLUMEDOWN:
                vol = self.audioPlayer.audio_get_volume()-VOL_INCDEC
                self.audioPlayer.audio_set_volume(vol)
            elif button == KeyConfig.AUDIOBUTTON_NEXT:
                self.audioPlayer.next_chapter()
            elif button == KeyConfig.AUDIOBUTTON_PREV:
                self.audioPlayer.previous_chapter()

    def playAudio(self, audio):
        if not self.audioPlayer is None:
            print("stopping current audio")
            self.audioPlayer.stop()
            self.states.enterMenu(MENUSTATE_IDLE)
        if audio is None:
            return
        self.states.enterMenu(MENUSTATE_PLAYING)
        print("start playing ", audio)
        self.audioPlayer = vlc.MediaPlayer(audio)
        self.audioPlayer.play()

    def startServer(self):
        print('Hello from the Nightstand Service')
        try:
            while True:
                # call the sync function call any triggered callbacks
                self.trellis.sync()
                # the trellis can only be read every 17 millisecons or so
                time.sleep(0.02)
        except:
            self.config.stop()
        self.stop()

    def startCLI(self):
        print('Hello from the Nightstand Server')
        self.reset()
        self.timer.start()
        try:
            while True:
                # call the sync function call any triggered callbacks
                self.trellis.sync()
                # the trellis can only be read every 17 millisecons or so
                time.sleep(0.02)
        except KeyboardInterrupt:
            self.config.stop()
        self.stop()

    def stop(self):
        self.config.join()
        self.timer.stop()
        self.states.unregisterMenuStateChangeListener(self.onMenuChanged)


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
