#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface
from pyHS100 import SmartPlug
from nodes import SmartDeviceNode

LOGGER = polyinterface.LOGGER

class SmartPlugNode(SmartDeviceNode):

    def __init__(self, controller, address, name, model, host):
        drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 78},
            {'driver': 'CC', 'value': 0, 'uom': 1}, #amps
            {'driver': 'CV', 'value': 0, 'uom': 72}, #volts
            {'driver': 'CPW', 'value': 0, 'uom': 73}, #watts
            {'driver': 'TPW', 'value': 0, 'uom': 33}, #kWH
            {'driver': 'GV0', 'value': 0, 'uom': 2} #connection state
        ]
        self.dev = SmartPlug(host)
        super().__init__(controller, controller.address, address, name, model, host)
        if self.dev.has_emeter:
            self.l_debug('__init__','Has emeter')
        else:
            self.l_debug('__init__','No emeter')

    def start(self):
        super().start()
        self.set_energy()

    def longPoll(self):
        super().longPoll()
        self.set_energy()

    def set_energy(self):
        if self.dev.has_emeter:
            try:
                energy = self.dev.get_emeter_realtime()
                if energy is not None:
                    # rounding the values reduces driver updating traffic for
                    # insignificant changes
                    self.setDriver('CC',round(energy['current'],3))
                    self.setDriver('CV',round(energy['voltage'],1))
                    self.setDriver('CPW',round(energy['power'],1))
                    self.setDriver('TPW',round(energy['total'],3))
            except:
                self.l_error('set_energy','failed', exc_info=True)

    def query(self):
        self.set_state()
        self.set_energy()
        self.reportDrivers()

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
