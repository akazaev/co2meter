#!/usr/bin/env python2
# coding: utf-8

import logging
import sys
import time

import sqlite3

from db import CREATE_CMD, ADD_ROW_CMD
from mhz19 import MHZ14Reader
from lcddrvier import LCD
from sygnals import Sygnals


def clean():
    lcd.lcd_clear()
    led_sygnals.stop_all()
    conn.disconnect()
    con.close()
    led_sygnals.exit()


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
    start_count = 0
    led_sygnals.change('blue', blink=True)

    current_level = None

    try:
        while True:
            status = conn.get_status()
            if status:
                ppm = status['ppm']
                zone = status['zone']
                temp = status['temp']
                response = status['response']

                if not start:
                    led_sygnals.power_on('blue')
                    time.sleep(1)
                    led_sygnals.power_off('blue')
                datetime = time.strftime('%Y-%m-%d %H:%M:%S')
                print '{0}, {1} ppm, {2} (temp {3})'.format(datetime, ppm,
                                                            zone, temp)
                cur.execute(ADD_ROW_CMD.format(datetime, ppm, str(response)))
                con.commit()
                logging.info(ppm)

                if start:
                    # blue blinks
                    if 400 <= ppm <= 2000:
                        led_sygnals.stop_all()
                        start = False
                    else:
                        start_count += 1
                        lcd.lcd_clear()
                        lcd.lcd_display_string('debug {0},{1}'.format(ppm,
                                                                      temp), 2)
                        time.sleep(0.2)
                        lcd.lcd_clear()
                        lcd.lcd_display_string('initialize...', 1)

                        # if no real data from sensor on start try to reconnect
                        if start_count >= 3:
                            start_count = 0
                            conn.disconnect()
                            conn = MHZ14Reader(port)
                            print '{0}, reconnect'.format(datetime)

                if not start:
                    # sygnals
                    new_level = None
                    if ppm <= 800:
                        new_level = 'green'
                    if 800 < ppm <= 1000:
                        new_level = 'yellow'
                    if ppm > 1000:
                        new_level = 'red'
                    if new_level != current_level:
                        current_level = new_level
                        is_blink = new_level != 'green'
                        led_sygnals.change(new_level,  blink=is_blink)

                    lcd.lcd_clear()
                    lcd.lcd_display_string('{0} ppm'.format(ppm), 1)
                    lcd.lcd_display_string('temp {0}'.format(temp), 2)
            else:
                print 'No data received'

            time.sleep(timeout - 1)
    except (KeyboardInterrupt, SystemExit):
        clean()
        sys.exit()
    except Exception as err:
        clean()
        logging.error(unicode(err))
