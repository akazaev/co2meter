# coding: utf-8

import time

from Queue import Queue

import sqlite3

from helpers import StoppableThread


CREATE_CMD = ('create table if not exists co2meter (time datetime, ppm '
              'integer, ppma integer, temp integer, response varchar(255))')

CREATE_PWM_CMD = ('create table if not exists co2meter_pwm (time datetime, '
                  'ppm integer)')

ADD_ROW_CMD = ('insert into co2meter (time, ppm, ppma, temp, response) '
               'values("{0}", {1}, {2}, {3}, "{4}")')

ADD_ROW_PWM_CMD = 'insert into co2meter_pwm (time, ppm) values("{0}", {1})'


class DBThread(StoppableThread):

    def __init__(self, db_path='/tmp/mhz19.db', queue=None):
        self.db_path = db_path
        self.queue = queue
        super(DBThread, self).__init__()

    def run(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_CMD)
        self.cur.execute(CREATE_PWM_CMD)
        self.con.commit()

        while not self.stopped():
            if not self.queue.empty():
                query = self.queue.get(block=False)
                self.exec_query(query)
            time.sleep(0.1)
        self.con.close()

    def exec_query(self, query):
        self.cur.execute(query)
        self.con.commit()


class DBManager(object):

    def __init__(self, db_path='/tmp/mhz19.db'):
        self.queue = Queue()
        self.thread = DBThread(db_path, self.queue)
        self.thread.start()

    def save_uart_data(self, status):
        datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        query = ADD_ROW_CMD.format(datetime, status['ppm'], status['ppm_pwm'],
                                   status['temp'], str(status['response']))
        self.queue.put(query)

    def save_pwm_data(self, datetime, ppm):
        query = ADD_ROW_PWM_CMD.format(datetime, ppm)
        self.queue.put(query)

    def exit(self):
        self.thread.stop()
        self.thread.join()
