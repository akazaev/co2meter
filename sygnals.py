# coding: utf-8

import time

from threading import Thread, Event

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)

LED_PINS = {
    'red': 32,
    'yellow': 36,
    'green': 38,
    'blue': 40,
}


class SygnalThread(Thread):
    led = None

    def __init__(self, event, blink=None, sleep=1):
        self.event = event
        self.sleep = sleep
        self.blink = blink and 1 or 0
        super(SygnalThread, self).__init__()

    def run(self):
        GPIO.setup(self.led, GPIO.OUT)
        GPIO.output(self.led, 1)
        while True:
            GPIO.output(self.led, 1)
            self.event.wait()
            GPIO.output(self.led, 0)
            time.sleep(self.sleep)
            GPIO.output(self.led, self.blink)
            time.sleep(self.sleep)


class RedSygnal(SygnalThread):
    led = LED_PINS['red']


class YellowSygnal(SygnalThread):
    led = LED_PINS['yellow']


class GreenSygnal(SygnalThread):
    led = LED_PINS['green']


class BlueSygnal(SygnalThread):
    led = LED_PINS['blue']


class Sygnals(object):

    def __init__(self):
        self.sygnals = {}
        _sygnals = {
            'red': RedSygnal,
            'yellow': YellowSygnal,
            'green': GreenSygnal,
            'blue': BlueSygnal,
        }
        for color, cls in _sygnals.items():
            # blink
            event = Event()
            instance = cls(event)
            self.sygnals[(color, 0)] = (instance, event)
            instance.start()

            # permanently
            event = Event()
            sleep = 0.5 if color in ['red', 'blue'] else 1
            instance = cls(event, blink=1, sleep=sleep)
            self.sygnals[(color, 1)] = (instance, event)
            instance.start()

    def start(self, color, blink=None):
        blink = blink and 1 or 0
        sygnal, event = self.sygnals[(color, blink)]
        event.set()

    def change(self, color, blink=None):
        blink = blink and 1 or 0
        self.stop_all()
        self.start(color, blink=blink)

    def stop_all(self):
        for color, sygnal in self.sygnals.items():
            _sygnal, event = sygnal
            event.clear()

    def stop(self, color, blink=None):
        blink = blink and 1 or 0
        sygnal, event = self.sygnals[(color, blink)]
        event.clear()

    def power_off(self, color):
        if color in LED_PINS:
            GPIO.setup(LED_PINS[color], GPIO.OUT)
            GPIO.output(LED_PINS[color], 1)

    def power_on(self, color):
        if color in LED_PINS:
            GPIO.setup(LED_PINS[color], GPIO.OUT)
            GPIO.output(LED_PINS[color], 0)
