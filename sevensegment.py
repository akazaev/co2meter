import time

from luma.core.serial import spi
from luma.core.render import canvas
from luma.led_matrix.device import max7219, sevensegment


class Sevensegment(object):

    def __init__(self):
        serial = spi(port=0, device=0)
        device = max7219(serial)
        self.seg = sevensegment(device)

        text = '-'
        for i in range(7):
            self.seg.text = text
            text = ' ' + text
            time.sleep(0.5)
        self.seg.text = '-'*8

    def set_output(self, ppm, temp):
        if self.seg:
            text = '%4s%4s' % (int(ppm), int(temp))
            self.seg.text = text
