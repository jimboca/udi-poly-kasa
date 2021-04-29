#
# TP Link Kasa Smart Plug Node
#
# This code is used for plugs
#
import polyinterface
from kasa import SmartPlug,SmartDeviceException

from nodes import SmartDeviceNode

LOGGER = polyinterface.LOGGER

class SmartPlugNode(SmartDeviceNode):

    def __init__(self, controller, address, name, cfg=None, dev=None):
        # All plugs have these.
        self.debug_level = 0
        self.name = name
        # All devices have these.
        self.drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 78},
            {'driver': 'GV0', 'value': 0, 'uom': 2}, #connection state
        ]
        if dev is not None:
            # Figure out the id based in the device info
            self.id = 'SmartPlug_'
            if dev.is_dimmable:
                self.id += 'D'
            else:
                self.id += 'N'
            if dev.has_emeter:
                self.id += 'E'
            else:
                self.id += 'N'
            cfg['emeter'] = dev.has_emeter
        if cfg['emeter']:
            self.drivers.append({'driver': 'CC', 'value': 0, 'uom': 56})
            self.drivers.append({'driver': 'CV', 'value': 0, 'uom': 56})
            self.drivers.append({'driver': 'CPW', 'value': 0, 'uom': 73})
            self.drivers.append({'driver': 'TPW', 'value': 0, 'uom': 73})
        super().__init__(controller, controller.address, address, name, dev, cfg)

    def start(self):
        super().start()
        self.set_energy()

    def longPoll(self):
        super().longPoll()
        self.set_energy()

    def newdev(self):
        return SmartPlug(self.host)

    def cmd_set_on(self,command):
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        super().cmd_set_off(command)

    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }

