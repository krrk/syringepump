#!/usr/bin/python

import serial
import logging

logging.basicConfig(level=logging.DEBUG)

class Model44(object):
    prompts = {
        b':': 'stopped',
        b'>': 'running',
        b'<': 'reverse',
        b'/': 'paused',
        b'*': 'stopped',
        b'^': 'wait', # dispense trigger wait
        }
    ranges = [ 'uL/min', 'mL/min', 'uL/hr' , 'mL/hr' ]

    def __init__(self, port=0, number=0):
        self.port  = serial.Serial(port, baudrate=9600, stopbits=2)
        self.pumpN = str(number)
        try:
            ver = self.get_version()
            logging.info('Connected to version {} Model44'.format(ver))
        except:
            self.last_status = 'stopped'

    def _write(self, cmd):
        logging.debug('write: {}'.format(cmd))
        self.port.write((self.pumpN+' '+cmd+'\r').encode('utf-16le'))

    def _read_reply(self):
        s = self.port.read(1)
        if s != b'\n':
            raise RuntimeError('Expected LF, saw "{}"'.format(s))
        
        reply = None
        prompt = None
        s = b''
        for i in range(50):
            s += self.port.read(1)
            if s[-1] == ord('\r'):
                reply = s.decode().strip()
            if len(s) >= 2 and s[-2:-1].isdigit() and s[-1:-2:-1] in Model44.prompts:
                prompt = Model44.prompts[s[-1:-2:-1]]
                break

        logging.debug("read: {}".format(s))
        if prompt == None:
            raise RuntimeError('Expected prompt, got "{}"'.format(s))
        else:
            self.last_status = prompt
        return reply

    def _read_value(self):
        s = self._read_reply()
        return float(s.strip())

    def _format_float(self, n):
        if n > 1e6: raise ArgumentError('Number too large')
        return ('{:06f}'.format(n))[:6]

    def __value_func(cmd):
        def f(self):
            self._write(cmd)
            return self._read_value()
        return f
    
    def __command_func(cmd):
        def f(self):
            self._write(cmd)
            self._read_reply()
        return f

    def get_version(self):
        self._write('VER')
        version = self._read_reply()
        return version
    
    def get_status(self):
        """ Get status of pump """
        return self.last_status

    def get_flow_rate(self):
        units = { 'ul/mn': 'uL/min',
                  'ml/mn': 'mL/min',
                  'ul/hr': 'uL/hr',
                  'ml/hr': 'mL/hr'}
        self._write('RAT')
        s = self._read_reply()
        value, unit = s.split()
        return float(value), units[unit]

    def get_mode(self):
        self._write('MOD')
        mode = self._read_reply()
        return mode.lower().strip()
    
    get_diameter       = __value_func('DIA')
    get_target_volume  = __value_func('TGT')
    get_volume_accum   = __value_func('DEL')

    start              = __command_func('RUN')
    stop               = __command_func('STP')
    clear_volume_accum = __command_func('CLD')
    clear_target       = __command_func('TGT 0')
    reverse            = __command_func('DIR REV')

    def set_diameter(self, value):
        """ Set diameter of syringe in millimeters """
        self._write('DIA ' + self._format_float(value))
        return self._read_reply()

    def set_direction(self, dir):
        d = 'INF' if dir > 0 else 'REF'
        self._write('DIR {}'.format(d))
        self._read_reply()

    def set_flow_rate(self, value, range):
        """ Set flow rate in given range """
        ranges = {
            'uL/min': 'UM',
            'mL/min': 'MM',
            'uL/hr' : 'UH',
            'mL/hr' : 'MH' }
        
        if range not in ranges:
            raise Exception("Invalid range")
        self._write("RAT {} {}".format(self._format_float(value), ranges[range]))
        self._read_reply()

    def set_target_volume(self, value):
        """ Set the target volume """
        self._write("TGT " + self._format_float(value))
        self._read_reply()

    def set_pump_mode(self):
        self._write('MOD PMP')
        self._read_reply()

    def set_volume_mode(self):
        self._write('MOD VOL')
        self._read_reply()
