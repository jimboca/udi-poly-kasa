#
# TP Link Kasa Smart Dimmer Node
#
# This code is used for dimmers (HS220)
#
import polyinterface,asyncio
from kasa import SmartPlug,SmartDimmer,SmartDeviceException
from converters import bri2st,st2bri

from nodes import SmartDeviceNode

LOGGER = polyinterface.LOGGER

class SmartDimmerNode(SmartDeviceNode):

    def __init__(self, controller, address, name, cfg=None, dev=None):
        # All plugs have these.
        self.debug_level = 0
        self.name = name
        # All devices have these.
        self.drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 51},
            {'driver': 'GV0', 'value': 0, 'uom': 2}, #connection state
        ]
        if dev is not None:
            # Figure out the id based in the device info
            self.id = 'SmartDimmer_'
            if dev.is_dimmable:
                self.id += 'D'
                self.drivers.append({'driver': 'GV5', 'value': 0, 'uom': 100})
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

    def set_bri(self,val):
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            self.brightness = int(val)
            LOGGER.debug(f'{val}')
            self.setDriver('GV5',self.brightness)
            # This won't actually change unless the device is on
            asyncio.run(self.dev.set_brightness(int(bri2st(self.brightness))))
            asyncio.run(self.dev.update())
            self.setDriver('ST',self.dev.brightness)

    def brt(self):
        LOGGER.debug(f'{self.pfx} connected={self.connected}')
        asyncio.run(self.dev.update())
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness <= 100:
            self.set_bri(self.brightness + 7)

    def dim(self):
        LOGGER.debug('{self.pfx} connected={self.connected}')
        asyncio.run(self.dev.update())
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness > 0:
            self.set_bri(self.brightness - 7)

    def newdev(self):
        return SmartDimmer(self.host)

    def cmd_set_on(self,command):
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        super().cmd_set_off(command)

    def cmd_set_bri(self,command):
        val = int(command.get('value'))
        LOGGER.info(f'{self.pfx} val={val}')
        asyncio.run(self.dev.turn_on())
        self.set_bri(val)

    def cmd_brt(self,command):
        if not self.dev.is_dimmable:
            LOGGER.error('{self.pfx} Not supported on this device')
        asyncio.run(self.dev.turn_on())
        self.brt()

    def cmd_dim(self,command):
        if not self.dev.is_dimmable:
            LOGGER.error('{self.pfx} Not supported on this device')
        self.dim()

    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
        'SET_BRI': cmd_set_bri,
        'BRT': cmd_brt,
        'DIM': cmd_dim,
    }

