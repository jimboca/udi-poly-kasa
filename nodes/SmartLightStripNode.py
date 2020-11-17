#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface,asyncio
from kasa import SmartLightStrip,SmartDeviceException
from nodes import SmartBulbNode

LOGGER = polyinterface.LOGGER

# LightSTrip is the same as bulb
# TODO: Add lenght Driver for info?

class SmartLightStripNode(SmartBulbNode):

    def __init__(self, controller, address, name, dev=None, cfg=None):
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
        else:
            self.id = cfg['id']
        if cfg['color_temp']:
            self.drivers.append({'driver': 'CLITEMP', 'value': 0, 'uom': 26})
        if cfg['color']:
            self.drivers.append({'driver': 'GV3', 'value': 0, 'uom': 100}) #hue
            self.drivers.append({'driver': 'GV4', 'value': 0, 'uom': 100}) #sat
        super().__init__(controller, address, name, dev, cfg)

    def newdev(self):
        return SmartLightStrip(self.host)
