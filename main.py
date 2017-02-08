#!/usr/bin/env python2
# coding: utf-8

import logging
import sys
import time

from db import DBManager
from mhz19 import MHZ14_UART, MHZ14_PWM
from lcddrvier import LCD
from sygnals import Sygnals


logging.getLogger().setLevel(logging.INFO)


def clean():
    if lcd:
        lcd.lcd_clear()
    led_sygnals.stop_all()
    conn.disconnect()
    conn_pwm.exit()
    db.exit()
    led_sygnals.exit()


if __name__ == '__main__':

    try:
        lcd = LCD(port=3)
    except Exception as err:
        logging.warning('Display is not available.')
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

    led_sygnals.power_on('blue')
    # wait pwm first data
    time.sleep(2)
    led_sygnals.power_off('blue')

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

                led_sygnals.power_on('blue')
                time.sleep(1)
                led_sygnals.power_off('blue')

                if 0 <= ppm <= 5000:
                    db.save_uart_data(status)

                logging.info('UART: {0} ppm, PWM: {1} ppm, temp {2}'
                             ''.format(ppm, ppm_pwm, temp))

                # sygnals
                new_level = None
                if ppm < 800:
                    new_level = 'green'
                if 800 <= ppm <= 1200:
                    new_level = 'yellow'
                if ppm > 1200:
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
        raise
