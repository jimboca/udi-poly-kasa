
import polyinterface
from nodes import SmartStripPlugNode

LOGGER = polyinterface.LOGGER

class SmartStripNode(polyinterface.Node):

    def __init__(self, controller, address, name, dev):
        self.dev = dev
        self.name = name
        self.debug_level = 0
        self.l_debug('__init__','controller={}'.format(controller))
        # The strip is it's own parent since the plugs are it's children
        super(SmartStripNode, self).__init__(self, address, address, name)
        self.controller = controller

    def start(self):
        self.setDriver('ST', 1)
        for pnum in range(self.dev.num_children):
            naddress = "{}{:02d}".format(self.address,pnum+1)
            nname    = self.dev.get_alias(index=pnum)
            self.l_info('start','adding plug num={} address={} name={}'.format(pnum,naddress,nname))
            self.controller.addNode(SmartStripPlugNode(self.controller, self, naddress, nname, pnum))

    def setOn(self, command):
        self.setDriver('ST', 1)

    def setOff(self, command):
        self.setDriver('ST', 0)

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

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]
    id = 'SmartStrip'
    commands = {
        'DON': setOn,
        'DOF': setOff
    }
