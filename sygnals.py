# coding: utf-8

import time

from threading import Thread, Event

import RPi.GPIO as GPIO


class SygnalThread(Thread):
    led = None

    def __init__(self, event, blink=None):
        self.event = event
        self.blink = blink and 1 or 0
        super(SygnalThread, self).__init__()

    def run(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.led, GPIO.OUT)
        GPIO.output(self.led, 1)
        while True:
            GPIO.output(self.led, 1)
            self.event.wait()
            GPIO.output(self.led, 0)
            time.sleep(1)
            GPIO.output(self.led, self.blink)
            time.sleep(1)


class RedSygnal(SygnalThread):
    led = 32


class YellowSygnal(SygnalThread):
    led = 36


class GreenSygnal(SygnalThread):
    led = 38


class BlueSygnal(SygnalThread):
    led = 40


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
            instance = cls(event, blink=1)
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
