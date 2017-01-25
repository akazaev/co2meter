#!/usr/bin/env python2
# coding: utf-8

import logging
import time

import sqlite3

from db import CREATE_CMD, ADD_ROW_CMD
from mhz19 import MHZ14Reader
from lcddrvier import LCD
from sygnals import Sygnals


if __name__ == '__main__':

    lcd = LCD(port=3)

    led_sygnals = Sygnals()
    led_sygnals.change('blue')

    con = sqlite3.connect('/tmp/mhz19.db')
    cur = con.cursor()
    cur.execute(CREATE_CMD)
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
                if not start:
                    led_sygnals.power_on('blue')
                    time.sleep(1)
                    led_sygnals.power_off('blue')
                datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                print '{0}, {1} ppm, {2} (temp {3})'.format(datetime,
                                                            status['ppm'],
                                                            status['zone'],
                                                            status['temp'])
                cur.execute(ADD_ROW_CMD.format(datetime, status['ppm'],
                                               str(status['response'])))
                con.commit()
                logging.info(status['ppm'])

                lcd.lcd_clear()
                lcd.lcd_display_string('{0} ppm'.format(status['ppm']), 1)
                lcd.lcd_display_string('temp {0}'.format(status['temp']), 2)

                if start:
                    # blue blinks
                    if 400 <= status['ppm'] <= 2000:
                        led_sygnals.stop_all()
                        start = False

                if not start:
                    # sygnals
                    new_level = None
                    if status['ppm'] <= 800:
                        new_level = 'green'
                    if 800 < status['ppm'] <= 1000:
                        new_level = 'yellow'
                    if status['ppm'] > 1000:
                        new_level = 'red'
                    if new_level != current_level:
                        current_level = new_level
                        is_blink = new_level != 'green'
                        led_sygnals.change(new_level,  blink=is_blink)
            else:
                print 'No data received'

            time.sleep(timeout - 1)

    except Exception as err:
        logging.error(unicode(err))
    finally:
        conn.disconnect()
        con.close()
