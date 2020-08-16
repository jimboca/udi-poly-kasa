
import polyinterface
from kasa import SmartStrip,SmartDeviceException
from nodes import SmartStripPlugNode

LOGGER = polyinterface.LOGGER

class SmartStripNode(polyinterface.Node):

    def __init__(self, controller, address, name, dev=None, cfg=None):
        self.ready = False
        self.name = name
        if dev is not None:
            self.host = dev.host
        else:
            self.host = cfg['host']
        self.debug_level = 0
        self.st = None
        self.pfx = f"{self.name}:"
        # Bug in current PyHS100 doesn't allow us to print dev.
        LOGGER.debug(f'{self.pfx} controller={controller} address={address} name={name} host={self.host}')
        # The strip is it's own parent since the plugs are it's children
        super(SmartStripNode, self).__init__(self, address, address, name)
        self.controller = controller

    def start(self):
        self.dev = SmartStrip(self.host)
        self.check_st()
        for pnum in range(len(self.dev.children)):
            naddress = "{}{:02d}".format(self.address,pnum+1)
            nname    = self.dev.get_alias(index=pnum)
            LOGGER.info(f"{self.pfx} adding plug num={pnum} address={naddress} name={nname}")
            self.controller.addNode(SmartStripPlugNode(self.controller, self, naddress, nname, pnum))
        self.ready = True

    def shortPoll(self):
        if not self.ready:
            return
        self.check_st()

    def check_st(self):
        if self.is_connected():
            self.setDriver('GV0',1)
        else:
            self.setDriver('GV0',0)
        is_on = False
        # If any are on, then I am on.
        for pnum in range(len(self.dev.children)):
            try:
                if self.dev.is_on(index=pnum):
                    is_on = True
            except Exception as ex:
                LOGGER.error('{self.pfx} failed', exc_info=True)
        self.set_st(is_on)

    def set_st(self,st):
        if st != self.st:
            if st:
                self.set_on()
            else:
                self.set_off()

    def is_connected(self):
        return True

    def set_on(self):
        self.setDriver('ST', 100)
        self.st = True

    def set_off(self):
        self.setDriver('ST', 0)
        self.st = False

    def query(self):
        self.reportDrivers()

    def cmd_set_on(self, command):
        self.set_on()

    def cmd_set_off(self, command):
        self.set_off()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 78},
        {'driver': 'GV0', 'value': 0, 'uom': 2}  # Connected
    ]
    id = 'SmartStrip'
    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }
