import time
import cwiid
import math
import random
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

class WiimoteController(QObject):
    '''
      Instances of this class should be run on their own thread,
      since polling is used.
    '''

    sig_button_pressed = pyqtSignal(int, str)
    sig_ready = pyqtSignal()

    def __init__(self, addresses):
        super(WiimoteController, self).__init__()
        self.addresses = addresses
        self.motes = []

    def start(self):
        while 1:
            print('Press 1&2 to configure...')
            time.sleep(1)
            if self.configure():
                self.sig_ready.emit()
                self.poll()
                break
            print('An error ocurred. Please, try again...')

    def configure(self):
        try:
            for address in self.addresses:
                self.motes.append(cwiid.Wiimote(address))

            for i, mote in enumerate(self.motes):
                mote.rpt_mode = cwiid.RPT_BTN
                # The LEDs represent a 4-bit binary number
                mote.led = 2**i
            return True
        except RuntimeError:
            return False

    def poll(self):
        while 1:
            random.shuffle(self.motes)
            for mote in self.motes:
                self._read_buttons(mote)

    def rumble(self, i, r):
        print('Rumble {} = {}'.format(i, r))
        self.motes[i].rumble = r

    def _read_buttons(self, mote):
        # See:
        # 0) http://www.brianhensley.net/2012/08/wii-controller-raspberry-pi-python.html
        # 1) http://wiigait.blogspot.com/2011/02/controlling-multiple-wiimotes-using.html
        # 2) http://www.raspberrypi-spy.co.uk/2013/02/nintendo-wii-remote-python-and-the-raspberry-pi/
        player = int(math.log(mote.state['led'], 2))
        buttons = mote.state['buttons']
        if (buttons & cwiid.BTN_LEFT):
            self.sig_button_pressed.emit(player, 'left')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_RIGHT):
            self.sig_button_pressed.emit(player, 'right')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_UP):
            self.sig_button_pressed.emit(player, 'up')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_DOWN):
            self.sig_button_pressed.emit(player, 'down')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_PLUS):
            self.sig_button_pressed.emit(player, 'plus')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_MINUS):
            self.sig_button_pressed.emit(player, 'minus')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_1):
            self.sig_button_pressed.emit(player, '1')
            time.sleep(0.5)
        if (buttons & cwiid.BTN_2):
            self.sig_button_pressed.emit(player, '2')
            time.sleep(0.5)
