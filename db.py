# coding: utf-8

import time

import sqlite3


CREATE_CMD = ('create table if not exists co2meter (time datetime, ppm '
              'integer, ppma integer, temp integer, response varchar(255))')

CREATE_PWM_CMD = ('create table if not exists co2meter_pwm (time datetime, '
                  'ppm integer)')

ADD_ROW_CMD = ('insert into co2meter (time, ppm, temp, response) '
               'values("{0}", {1}, {2}, "{3}")')

ADD_ROW_PWM_CMD = 'insert into co2meter_pwm (time, ppm) values("{0}", {1})'


class DBManager(object):

    def __init__(self, db_path='/tmp/mhz19.db'):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_CMD)
        self.cur.execute(CREATE_PWM_CMD)
        self.con.commit()

    def save_uart_data(self, status):
        datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cur.execute(ADD_ROW_CMD.format(datetime, status['ppm'],
                                            status['ppm_pwm'], status['temp'],
                                            str(status['response'])))
        self.con.commit()

    def save_pwm_data(self, status):
        datetime = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cur.execute(ADD_ROW_PWM_CMD.format(datetime, status['ppm']))
        self.con.commit()

    def exit(self):
        self.con.close()
