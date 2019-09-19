
import polyinterface
from pyHS100 import (SmartStrip)
from nodes import SmartStripPlugNode

LOGGER = polyinterface.LOGGER

class SmartStripNode(polyinterface.Node):

    def __init__(self, controller, address, name, host):
        self.host = host
        self.name = name
        self.debug_level = 0
        self.st = None
        # Bug in current PyHS100 doesn't allow us to print dev.
        self.l_debug('__init__','controller={} address={} name={} host={}'.format(controller,address,name,host))
        # The strip is it's own parent since the plugs are it's children
        super(SmartStripNode, self).__init__(self, address, address, name)
        self.controller = controller

    def start(self):
        self.dev = SmartStrip(self.host)
        self.check_st()
        for pnum in range(self.dev.num_children):
            naddress = "{}{:02d}".format(self.address,pnum+1)
            nname    = self.dev.get_alias(index=pnum)
            self.l_info('start','adding plug num={} address={} name={}'.format(pnum,naddress,nname))
            self.controller.addNode(SmartStripPlugNode(self.controller, self, naddress, nname, pnum))

    def shortPoll(self):
        self.check_st()

    def check_st(self):
        is_on = False
        # If any are on, then I am on.
        for pnum in range(self.dev.num_children):
            if self.dev.is_on(index=pnum):
                is_on = True
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

    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))

    def l_error(self, name, string, exc_info=False):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))

    def l_debug(self, name, string, level=0, exc_info=False):
        if level <= self.debug_level:
            LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

    def cmd_set_on(self, command):
        self.set_on()

    def cmd_set_off(self, command):
        self.set_off()

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78}]
    id = 'SmartStrip'
    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }
