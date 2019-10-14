#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface
from pyHS100 import SmartBulb
from nodes import SmartDeviceNode
from converters import RGB_2_xy, color_xy, bri2st, kel2mired

LOGGER = polyinterface.LOGGER

class SmartBulbNode(SmartDeviceNode):

    def __init__(self, controller, address, name, dev=None, cfg=None):
        self.name = name
        self.debug_level = 0
        self.drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 78},
            {'driver': 'GV0', 'value': 0, 'uom': 2},  #connection state
            {'driver': 'GV1', 'value': 0, 'uom': 100}, #brightness
        ]
        if dev is not None:
            # Figure out the id based in the device info
            self.id = 'SmartBulb_'
            if dev.is_dimmable:
                self.id += 'D'
            else:
                self.id += 'N'
            if dev.is_variable_color_temp:
                self.id += 'T'
            else:
                self.id += 'N'
            if dev.is_color:
                self.id += 'C'
            else:
                self.id += 'N'
            if dev.has_emeter:
                self.id += 'E'
            else:
                self.id += 'N'
            cfg['emeter'] = dev.has_emeter
            cfg['color']  = dev.is_color
            cfg['color_temp'] = dev.is_variable_color_temp
        if cfg['color_temp']:
            self.drivers.append({'driver': 'GV2', 'value': 0, 'uom': 56})
        if cfg['color']:
            self.drivers.append({'driver': 'GV3', 'value': 0, 'uom': 100}) #hue
            self.drivers.append({'driver': 'GV4', 'value': 0, 'uom': 100}) #sat
        super().__init__(controller, controller.address, address, name, dev, cfg)

    def set_all_drivers(self):
        self.l_info('set_all_drivers','brightness={}'.format(self.dev.brightness))
        if int(self.getDriver('GV1')) != self.dev.brightness:
            self.setDriver('GV1',self.dev.brightness)
        #is_variable_color_temp
        #if self.is_color:


    def newdev(self):
        return SmartBulb(self.host)

    def cmd_set_on(self,command):
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        super().cmd_set_off(command)

    def cmd_set_bri(self,command):
        super().cmd_set_bri(command)

    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
        'BRI': cmd_set_bri,
    }
