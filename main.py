#!/usr/bin/env python2
# coding: utf-8

import logging
import time

import sqlite3

from mhz19 import MHZ14Reader
from sygnals import Sygnals


if __name__ == '__main__':

    led_sygnals = Sygnals()
    led_sygnals.change('blue')

    con = sqlite3.connect('/tmp/mhz19.db')
    cur = con.cursor()
    cur.execute('create table if not exists co2meter '
                '(time datetime, ppm integer, response varchar(255))')
    con.commit()

    timeout = 10
    port = '/dev/ttyS0'

    conn = MHZ14Reader(port)
    print 'Connected to {0}'.format(conn.link.name)
    logging.info(conn.link.name)

    start = True
    led_sygnals.change('blue', blink=True)

    current_level = None

    try:
        while True:
            status = conn.get_status()
            if status:
                datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                print '{0}, {1} ppm, {2} (temp {3})'.format(datetime, status['ppm'],
                                                 status['zone'], status['temp'])
                cur.execute('insert into co2meter (time, ppm, response) '
                            'values("{0}", {1}, "{2}")'.format(datetime,
                                status['ppm'], str(status['response'])))
                con.commit()
                logging.info(status['ppm'])

                # sygnals
                if not start:
                    new_level = None
                    if status['ppm'] <= 700:
                        new_level = 'green'
                    if status['ppm'] > 700 and status['ppm'] <= 1000:
                        new_level = 'yellow'
                    if status['ppm'] > 1000:
                        new_level = 'red'
                    if new_level != current_level:
                        current_level = new_level
                        is_blink = new_level != 'green'
                        led_sygnals.change(new_level,  blink=is_blink)

                # start blink
                if start and status['ppm'] >= 400 and status['ppm'] <= 2000:
                    led_sygnals.stop_all()
                    start = False
            else:
                print 'No data received'

            time.sleep(timeout)
    except Exception as err:
        logging.error(unicode(err))
    finally:
        conn.disconnect()
        con.close()
