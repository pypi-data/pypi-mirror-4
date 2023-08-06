#!/bin/python
#
#    Python tool for interfacing the CEM DT-174B Weather Datalogger.
#    Copyright (C) 2013 Jaroslav Henner
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
import argparse
import logging
from collections import namedtuple
from struct import pack, unpack
from contextlib import contextmanager
from itertools import islice

import usb
import usb.core
import usb.util

DESCRIPTION = (
    "Python tool for interfacing the CEM DT-174B Weather Datalogger."
)

VENDOR, PRODUCT = 0x10c4, 0xea61

REQTYPE_HOST_TO_INTERFACE = 0x41
REQTYPE_INTERFACE_TO_HOST = 0xc1
REQTYPE_HOST_TO_DEVICE = 0x40
REQTYPE_DEVICE_TO_HOST = 0xc0

FORMAT  = '!' + 'BBBBBHBBB' + 'BBHB' 'hh' 'HH' 'hh' 'BhH'
XFORMAT = '!' + 'BBBBBHxxx' + 'BBHB' 'hh' 'HH' 'hh' 'xhH'


_Settings = namedtuple('SettingsPacket', '''
    year month day hour min sec
    rec_int alm_int smpl_int auto
    temp_high temp_low hum_high hum_low
    pressure_high pressure_low
    alt samples
''')


class SettingsPacket(_Settings):
    def pack(self):
        return pack(FORMAT,
                self.sec, self.min, self.hour,              # pylint: disable=E1101
                self.day, self.month, self.year,            # pylint: disable=E1101
                0xff, 0xff, 0xff,
                self.rec_int if self.rec_int else 0xff,     # pylint: disable=E1101
                self.alm_int if self.alm_int else 0xff,     # pylint: disable=E1101
                self.smpl_int, self.auto,                   # pylint: disable=E1101
                self.temp_high * 100, self.temp_low * 100,  # pylint: disable=E1101
                self.hum_high * 10, self.hum_low * 10,      # pylint: disable=E1101
                self.pressure_high * 10 - 10132,            # pylint: disable=E1101
                self.pressure_low  * 10 - 10132,            # pylint: disable=E1101
                0x5a,
                self.alt, self.samples)                     # pylint: disable=E1101

    @classmethod
    def unpack(cls, s):
        packet = unpack(XFORMAT, s)
        return cls(*packet)


def split_every(n, iterable):
    i = iter(iterable)
    while True:
        piece = list(islice(i, n))
        if not piece:
            break
        yield piece


def data_parser(reader):
    for packet in reader:
        pressure, temp, hum = unpack('hHh', packet)
        yield (pressure - 10132) * 10, temp * 100, hum * 10


class DT174BError(Exception):
    pass


class DT174B(object):
    def __init__(self):
        self.LOGGER = logging.getLogger('DT174B')
        self.start()

    def start(self):
        # Find our device.
        self.dev = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
        if self.dev is None:
            raise DT174BError('Device %s:%s not found.', VENDOR, PRODUCT)

        # Try detaching the kernel driver.
        try:
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
        except usb.USBError as e:
            self.LOGGER.warning("Couldn't detach the kernel driver: %s", e)

        self.dev.set_configuration()
        self.cfg = self.dev.get_active_configuration()
        self.iep, self.oep = self._get_eps()

    def reset(self):
        # NOTE: [http://libusb.sourceforge.net/doc/function.usbreset.html]
        # Causes re-enumeration: After calling usb_reset, the device will 
        # need to re-enumerate and thusly, requires you to find the new device 
        # and open a new handle. The handle used to call usb_reset will no 
        # longer work.
        self.dev.reset()
        self.start()

    def read_log(self):
        BUF_SIZE = 128
        LOGGER = logging.getLogger('DT174B.read_log')
        OK_RESPONSE = 'fe0100'.decode('hex')

        with self._known_state():
            # Retrieve the settings packet.
            self._write_oep(pack('BBB', 0x0f, 0, 0))

            cmd, total = unpack('>BH', self._read_iep(BUF_SIZE))

            settings_pkt = self._read_iep(BUF_SIZE)
            LOGGER.debug(settings_pkt.encode('hex'))

            # Parse the settings packet.
            settings = SettingsPacket.unpack(settings_pkt)
            LOGGER.info('Settings: %s', settings)

            i = 0
            remaining = total
            while 0 < remaining:
                i += 1
                wdata = pack('BBB', 0x0f, i, 0)
                self._write_oep(wdata)
                assert OK_RESPONSE == self._read_iep(BUF_SIZE)
                LOGGER.info('Bytes remaining: %d, read %s, total %s.', 
                            remaining, total - remaining, total)
                try:
                    for _ in range(4):
                        if remaining <= 0:
                            break
                        buf = self._read_iep(BUF_SIZE, timeout=100)
                        remaining -= len(buf)
                        yield buf
                except usb.USBError as e:
                    if e.message != 'Operation timed out':
                        raise
            LOGGER.info('Bytes remaining: %d, read %s, total %s.', 
                        remaining, total - remaining, total)

    @contextmanager
    def _known_state(self):
        try:
            self.LOGGER.info('Setting device to state 0x2.')
            self._send_control(REQTYPE_HOST_TO_DEVICE, 2, 0x2)
            yield
        finally:
            self.LOGGER.info('Setting device to state 0x4.')
            self._send_control(REQTYPE_HOST_TO_DEVICE, 2, 0x4)

    def send_settings(self, packet):
        LOGGER = logging.getLogger('DT174B.send_settings')
        try:
            self._send_control(REQTYPE_HOST_TO_DEVICE, 0, 0xffff)
        except usb.USBError:
            # Pipe Error
            pass
        iep, oep = self._get_eps()
        self._send_control(REQTYPE_HOST_TO_DEVICE, 2, 0x2)
        assert 3 == self._write_oep('0e4000'.decode('hex'))
        LOGGER.debug('> %s', self._write_oep(packet.pack()))
        assert '\xff' == iep.read(256).tostring()
        self._send_control(REQTYPE_HOST_TO_DEVICE, 2, 0x4)

    def _get_eps(self):
        interface_number = self.cfg[(0, 0)].bInterfaceNumber
        alternate_setting = usb.control.get_interface(
                self.dev, interface_number)
        self.intf = intf = usb.util.find_descriptor(
            self.cfg, bInterfaceNumber = interface_number,
            bAlternateSetting = alternate_setting
        )

        iep = usb.util.find_descriptor(
            intf,
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN
        )
        oep = usb.util.find_descriptor(
            intf,
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT
        )
        assert all((iep, oep))
        return iep, oep

    def _send_control(self, *args, **kwargs):
        '''
        params: see ctrl_transfer
        bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None
        '''
        LOGGER = logging.getLogger('DT174B.control')
        try:
            self.dev.ctrl_transfer(*args, **kwargs)
        except usb.USBError as e:
            if e.errno != 32:
                raise
            else:
                LOGGER.error(e)

    def _write_oep(self, data):
        LOGGER = logging.getLogger('DT174B.write')
        LOGGER.debug('> %s', data.encode('hex'))
        self.oep.write(data)

    def _read_iep(self, *args, **kwargs):
        data = self.iep.read(*args, **kwargs).tostring()
        LOGGER = logging.getLogger('DT174B.read')
        LOGGER.debug('< %s', data.encode('hex'))
        return data

    def __del__(self):
        self.close()

    def close(self):
        usb.util.release_interface(self.dev, self.intf)


class AbstractAction(object):
    __metaclass__ = ABCMeta
    def register(self, subparser):
        parser = subparser.add_parser(self.name,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                    help=self.help)
        parser.set_defaults(func=self)
        self.add_options(parser)

    def add_options(self, parser):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class SetAction(AbstractAction):
    name = 'set'
    help = 'Set and start the logging.'

    def add_options(self, parser):
        parser.add_argument('--rec_int', default=10,
                help='REC LED blinking interval')
        parser.add_argument('--alm_int', default=10,
                help='ALM LED bLinking interval')
        parser.add_argument('--smpl_int', default=1,
                help='Sampling interval')
        parser.add_argument('--auto', action='store_true',
                help='Whether to automaticaly start loging.')
        return
        self.temp_high * 100, self.temp_low * 100,
        self.hum_high * 10, self.hum_low * 10,
        self.pressure_high * 10 - 10132,
        self.pressure_low  * 10 - 10132,
        0x5a,
        self.alt, self.samples

    def __call__(self, args):
        raise NotImplementedError()
        DT174B().send_settings() # TODO


class DownloadAction(AbstractAction):
    name = 'download'
    help = 'Download the log.'

    def __call__(self, args):
        logger = DT174B()
        logger.reset()
        for line in logger.read_log():
            print line.encode('hex')


def module_relative_path(path):
    import os.path
    return os.path.join(os.path.dirname(__file__), path)


def setup_logging():
    import logging.config
    import yaml
    with open(module_relative_path('logging.conf'), 'r') as logging_config:
        D = yaml.load(logging_config)
    D.setdefault('version', 1)
    logging.config.dictConfig(D)


def main():
    import sys
    setup_logging()

    parser = argparse.ArgumentParser(description=DESCRIPTION,
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(help='sub-command help')
    for action in (SetAction(), DownloadAction()):
        action.register(subparsers)
    opts = parser.parse_args()
    try:
        opts.func(opts)
    except usb.core.USBError as err:
        if 'Access denied' in unicode(err):
            print >>sys.stderr
            print >>sys.stderr, err
            print >>sys.stderr, ('Perhaps you need to get added to the user '
                                 'group "datalogger", or you need root '
                                 'priviledges.')
            print >>sys.stderr
            sys.exit(err.args[0])
        else:
            raise


if __name__ == '__main__':
    main()

