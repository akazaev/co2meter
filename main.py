#!/usr/bin/env python2
# coding: utf-8

import logging
import sys
import time

from db import DBManager
from mhz19 import MHZ14_UART, MHZ14_PWM
from lcddrvier import LCD
from sygnals import Sygnals


def clean():
    if lcd:
        lcd.lcd_clear()
    led_sygnals.stop_all()
    conn.disconnect()
    db.exit()
    led_sygnals.exit()
    conn_pwm.exit()


if __name__ == '__main__':

    try:
        lcd = LCD(port=3)
    except Exception as err:
        logging.error(err)
        lcd = None

    db = DBManager()

    led_sygnals = Sygnals()
    led_sygnals.change('blue')

    timeout = 10
    port = '/dev/ttyS0'

    conn = MHZ14_UART(port)
    conn_pwm = MHZ14_PWM(db)
    print 'Connected to {0}'.format(conn.link.name)
    logging.info(conn.link.name)

    start = True
    start_count = 0
    led_sygnals.change('blue', blink=True)

    current_level = None

    try:
        while True:
            status = conn.get_status()
            status_pwm = conn_pwm.get_status()
            if status:
                ppm = status['ppm']
                ppm_pwm = status_pwm['ppm']
                status['ppm_pwm'] = ppm_pwm
                temp = status['temp']
                response = status['response']

                if not start:
                    led_sygnals.power_on('blue')
                    time.sleep(1)
                    led_sygnals.power_off('blue')
                print '{0} ppm ({1}), temp {2}'.format(ppm, ppm_pwm, temp)
                if not start:
                    db.save_uart_data(status)
                    logging.info(ppm)

                if start:
                    # blue blinks
                    if 400 <= ppm <= 2000:
                        led_sygnals.stop_all()
                        start = False
                    else:
                        start_count += 1
                        if lcd:
                            lcd.lcd_clear()
                            lcd.lcd_display_string('debug {0},{1}'.format(
                                ppm, temp), 2)
                            time.sleep(0.2)
                            lcd.lcd_clear()
                            lcd.lcd_display_string('initialize...', 1)

                        # if no real data from sensor on start try to reconnect
                        if start_count >= 3:
                            start_count = 0
                            conn.disconnect()
                            conn = MHZ14_UART(port)
                            print 'reconnect'

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

                    if lcd:
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
