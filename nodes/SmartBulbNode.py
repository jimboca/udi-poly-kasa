#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface
from pyHS100 import SmartBulb
from nodes import SmartDeviceNode

LOGGER = polyinterface.LOGGER

class SmartBulbNode(SmartDeviceNode):

    def __init__(self, controller, address, name, model, host):
        super().__init__(controller, controller.address, address, name, model, host)

    def newdev(self):
        return SmartBulb(self.host)

    def cmd_set_on(self,command):
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        super().cmd_set_off(command)

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'GV0', 'value': 0, 'uom': 2} #connection state
    ]
    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }
