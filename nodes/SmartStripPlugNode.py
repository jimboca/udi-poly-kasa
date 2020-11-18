
import polyinterface
import asyncio

LOGGER = polyinterface.LOGGER


class SmartStripPlugNode(polyinterface.Node):

    def __init__(self, controller, parent, address, name, dev):
        self.name = name
        self.dev = dev
        self.debug_level = 0
        self.pobj = parent # super changes self.parent
        # The strip is the parent since the plugs are it's children
        super(SmartStripPlugNode, self).__init__(self, parent.address, address, name)
        self.controller = controller

    def start(self):
        #self.setDriver('ST', 100)
        self.query()

    def shortPoll(self):
        self.check_st()

    def set_on(self):
        self.setDriver('ST', 100)

    def set_off(self):
        self.setDriver('ST', 0)

    def check_st(self):
        LOGGER.debug(f'{self.dev.alias}:check_st: is_on={self.dev.is_on}')
        if self.dev.is_on is True:
            self.setDriver('ST', 100)
        else:
            self.setDriver('ST', 0)

    def is_connected(self):
        return True

    def query(self):
        self.check_st()
        self.reportDrivers()

    def update(self):
        self.pobj.update()

    def cmd_set_on(self, command):
        LOGGER.debug(f'{self.dev.alias}:cmd_set_on: is_on={self.dev.is_on}')
        self.set_on()
        asyncio.run(self.dev.turn_on())

    def cmd_set_off(self, command):
        LOGGER.debug(f'{self.dev.alias}:cmd_set_off: is_on={self.dev.is_on}')
        self.set_off()
        asyncio.run(self.dev.turn_off())

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
        'DON': cmd_set_on,
        'DOF': cmd_set_off
    }
