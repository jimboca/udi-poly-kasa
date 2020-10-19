
import polyinterface
import asyncio

LOGGER = polyinterface.LOGGER


class SmartStripPlugNode(polyinterface.Node):

    def __init__(self, controller, parent, address, name, dev):
        self.name = name
        self.dev = dev
        self.debug_level = 0
        self.pobj = parent # super changes self.parent
        # The strip is it's own parent since the plugs are it's children
        super(SmartStripPlugNode, self).__init__(self, parent.address, address, name)
        self.controller = controller

    def start(self):
        #self.setDriver('ST', 100)
        self.query()

    def shortPoll(self):
        self.check_st()

    def setOn(self, command):
        self.setDriver('ST', 100)
        asyncio.run(self.dev.turn_on())

    def setOff(self, command):
        self.setDriver('ST', 0)
        asyncio.run(self.dev.turn_off())

    def check_st(self):
        if self.dev.is_on:
            self.setDriver('ST', 100)
        else:
            self.setDriver('ST', 0)

    def is_connected(self):
        return True

    def query(self):
        self.check_st()
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

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78}]
    id = 'SmartStripPlug'
    commands = {
        'DON': setOn,
        'DOF': setOff
    }
