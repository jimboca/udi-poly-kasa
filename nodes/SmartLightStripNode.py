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
        super().__init__(controller, address, name, dev, cfg)
        self.id = 'SmartLightStrip_'

    def newdev(self):
        return SmartLightStrip(self.host)
