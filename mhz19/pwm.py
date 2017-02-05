import time

from multiprocessing import Process, Queue, Event
from threading import Thread, Event

import RPi.GPIO as GPIO


class pwm_process(Process):

    def __init__(self, queue=None, pwm_port=18):
        self.pwm_port = pwm_port
        self.queue = queue
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pwm_port, GPIO.IN)
        self.exit_event = Event()
        super(pwm_process, self).__init__()

    def stop(self):
        self.exit_event.set()

    def stopped(self):
        return self.exit_event.is_set()

    def run(self):

        # initialize
        while not GPIO.input(self.pwm_port):
            time.sleep(0.0001)
        while GPIO.input(self.pwm_port):
            time.sleep(0.0001)

        try:
            while not self.stopped():
                # wait while low level
                while not GPIO.input(self.pwm_port):
                    time.sleep(0.0001)
                start = time.time()
                # wait while high level
                while GPIO.input(self.pwm_port):
                    time.sleep(0.0001)
                duration = time.time() - start
                ppm = int(round(5 * (duration*1000 - 2)))
                status = time.strftime('%Y-%m-%d %H:%M:%S'), ppm
                self.queue.put(status)
        except:
            pass


class StoppableThread(Thread):

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class pwm_thread(StoppableThread):

    ppm = 0

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.queue = Queue()
        self.process = pwm_process(self.queue)

        self.process.start()

        super(pwm_thread, self).__init__()

    def stop(self):
        self.process.stop()
        self.process.join()
        super(pwm_thread, self).stop()

    def run(self):
        while not self.stopped():
            if not self.queue.empty():
                datetime, self.ppm = self.queue.get(block=False)
                self.db_connection.save_pwm_data(datetime, self.ppm)
            time.sleep(0.1)


class MHZ14_PWM(object):

    def __init__(self, db_connection):
        self.db_connection = db_connection

        self.thread = pwm_thread(self.db_connection)
        self.thread.start()

    def exit(self):
        self.thread.stop()
        self.thread.join()

    def get_status(self):
        status = {'ppm': self.thread.ppm}
        return status
