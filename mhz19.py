# coding: utf-8

import logging
import serial

logger = logging.getLogger(__name__)


class MHZ14Reader:

    _requestSequence = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

    def __init__(self, port, open_connection=True):
        """
        :param string port: path to tty
        :param bool open_connection: should port be opened immediately
        """
        self.port = port
        """TTY name"""
        self.link = None
        """Connection with sensor"""
        if open_connection:
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

    def get_co2_level(self, ppm):
        level = 'Unknown'
        if ppm <= 450:
            level = 'Normal outdoor level'
        elif ppm <= 600:
            level = 'Acceptable level'
        elif ppm <= 1000:
            level = 'Complaints of stiffness and odors'
        elif ppm <= 2500:
            level = 'General drowsiness'
        elif ppm <= 5000:
            level = 'Adverse health effects may be expected'
        return level

    def get_status(self):
        """
        Read data from sensor
        :return {ppa, t}|None:
        """
        self._send_data_request()
        response = self.link.read(9)
        if len(response) == 9:
            ppm = ord(response[2]) * 0xff + ord(response[3])
            return {
                'ppm': ppm,
                'temp': ord(response[4]) - 40,
                'response': [ord(value) for value in response],
                'zone': self.get_co2_level(ppm)
            }

