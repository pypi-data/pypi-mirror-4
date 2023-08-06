#!/usr/bin/env python

## Python module for working with NooLite USB stick

## Last version at: https://github.com/Sicness/pyNooLite

import usb.core

__author__ = "Anton Balashov"
__license__ = "GPL v3"
__maintainer__ = "Anton Balashov"
__email__ = "Sicness@darklogic.ru"

class NooLiteErr(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class NooLite:
    _init_command = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    def __init__(self, channals=8, idVendor=0x16c0, idProduct=0x05df):
        if (type(idVendor) != type(int())) or (type(idProduct)) != type(int()):
            raise ValueError("idVendor and idProduct must has int type")
        if type(channals) != type(int()):
            raise ValueError("channals must has int type")
        self._idVendor = idVendor
        self._idProduct = idProduct
        self._channales = channals
        self._cmd = self._init_command

    def _set_ch(self, ch):
        try:
            ch = int(ch)
        except ValueError:
            raise ValueError("channal has %s can't be converted to int" % (type(ch)))
        if (ch > self._channales) or (ch < 0):
            raise NooLiteErr("Can't work with %d channal" % (ch))
        self._cmd[4] = ch

    def _send(self):
        dev = usb.core.find(idVendor = self._idVendor, idProduct = self._idProduct)  # find NooLite usb device
        if dev is None:
            raise NooLiteErr("Can find device with idVendor=%d idProduct=%d"
                             % (self._idVendor, self._idProduct))
        if dev.is_kernel_driver_active(0) is True:
            dev.detach_kernel_driver(0)
        dev.set_configuration()
        dev.ctrl_transfer(0x21, 0x09, 0, 0, self._cmd)
        return 0

    def on(self, ch):
        """Turn power on on channel
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x02       # "Turn power on" command
        if self._set_ch(ch):
            return -2
        return self._send()

    def off(self, ch):
        """Turn power off on channel
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x00       # "Turn power off" command
        if self._set_ch(ch):
            return -2
        return self._send()

    def set(self, ch, level):
        """Set brightness level
        Max level is 120
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x06       # "Turn power on" command
        if self._set_ch(ch):
            return -2
        self._cmd[2] = 0x01       # send level
        return self._send()

        # level in cmd must be in [0, 35 - 155]
        if level == 0:
            cmd[5] = 0
        elif level > 120:
            cmd[5] = 155
        else:
            cmd[5] = 35 + lvl
        return self._send()

    def bind(self, ch):
        """ Send bind signal on channel
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x0f       # "bind" command
        if self._set_ch(ch):
            return -2
        return self._send()

    def unbind(self, ch):
        """ Send unbind signal on channel
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x0f       # "unbind" command
        if self._set_ch(ch):
            return -2
        return self._send()

    def switch(self, ch):
        """switch power between off and on on channel
        First channal is 0 """
        self._cmd = self._init_command
        self._cmd[1] = 0x04       # "switch" command
        if self._set_ch(ch):
            return -2
        return self._send()
