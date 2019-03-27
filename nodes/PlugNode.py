
import polyinterface

LOGGER = polyinterface.LOGGER


class PlugNode(polyinterface.Node):

    def __init__(self, controller, parent, address, name, index):
        self.name = name
        self.index = index
        self.debug_level = 0
        # The strip is it's own parent since the plugs are it's children
        super(PlugNode, self).__init__(self, parent.address, address, name)
        self.controller = controller

    def start(self):
        self.setDriver('ST', 1)

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
    id = 'Plug'
    commands = {
        'DON': setOn,
        'DOF': setOff
    }
