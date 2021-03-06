# coding: utf-8

import logging
import time
import serial


class MHZ14_UART(object):

    _requestSequence = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

    def __init__(self, port):
        self.port = port
        self.link = None
        self.connect()

    def connect(self):
        """
        Open tty connection to sensor
        """
        if self.link is not None:
            self.disconnect()
        self.link = serial.Serial(self.port, 9600, bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE, dsrdtr=True,
                                  timeout=5, interCharTimeout=0.1)

        trash_byte = self.link.read(1)
        while trash_byte:
            logging.warning('read trash byte {0} from UART...'
                            ''.format(hex(ord(trash_byte))))
            trash_byte = self.link.read(1)

    def disconnect(self):
        """
        Terminate sensor connection
        """
        if self.link:
            self.link.close()

    def _send_data_request(self):
        """
        Send data request control sequence
        """
        for byte in self._requestSequence:
            self.link.write(chr(byte))

    def get_status(self):
        self._send_data_request()
        response = self.link.read(9)
        if len(response) == 9:
            ppm = ord(response[2]) * 0xff + ord(response[3])
            return {
                'ppm': ppm,
                'temp': ord(response[4]) - 40,
                'response': [ord(value) for value in response],
            }
