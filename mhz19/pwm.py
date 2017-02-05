import time

from multiprocessing import Process, Queue, Event

import RPi.GPIO as GPIO


class pwm_process(Process):

    def __init__(self, queue=None, pwm_port=18):
        self.pwm_port = pwm_port
        self.queue = queue
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


class MHZ14_PWM(object):

    def __init__(self, db_connection):
        self.db_connection = db_connection

        self.queue = Queue()
        self.process = pwm_process(self.queue)

        self.process.start()

    def exit(self):
        self.process.stop()
        self.process.join()

    def get_status(self):

        status = {'ppm': None}
        while not self.queue.empty():
            _datetime, ppm = self.queue.get(block=False)
            status = {'ppm': ppm}
            self.db_connection.save_pwm_data(status)
        return status
