# coding: utf-8

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

LED_PINS = {
    'red': (32, 2, 30),
    'yellow': (36, 1, 50),
    'green': (38, 1, 0),
}


class Sygnals(object):

    def __init__(self):
        self.sygnals = {}

        for color, pwm in LED_PINS.items():
            pin, freq, _cycle = pwm
            GPIO.setup(pin, GPIO.OUT)
            sygnal = GPIO.PWM(pin, freq)
            self.sygnals[color] = sygnal

        self.stop_all()

    def change(self, color):
        self.stop_all()
        _pin, _freq, cycle = LED_PINS[color]
        sygnal = self.sygnals[color]
        sygnal.start(cycle)

    def stop_all(self):
        for color, sygnal in self.sygnals.items():
            sygnal.start(100)

    def exit(self):
        self.stop_all()
        for color, sygnal in self.sygnals.items():
            sygnal.stop()
