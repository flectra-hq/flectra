# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

import platform
from serial.tools.list_ports import comports

from flectra.addons.hw_drivers.interface import Interface


class SerialInterface(Interface):
    connection_type = 'serial'

    def get_devices(self):
        serial_devices = {
            port.device: {'identifier': port.device}
            for port in comports()
            if platform.system() == 'Windows' or port.subsystem != 'amba'
            # RPI 5 uses ttyAMA10 as a console serial port for system messages: flectra interprets it as scale -> avoid it
        }
        return serial_devices
