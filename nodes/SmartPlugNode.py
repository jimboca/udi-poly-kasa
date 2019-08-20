
import polyinterface
#from nodes import SmartStripPlugNode

LOGGER = polyinterface.LOGGER

class SmartPlugNode(polyinterface.Node):

    def __init__(self, controller, address, name, dev):
        self.dev = dev
        self.name = name
        self.debug_level = 0
        self.st = None
        self.l_debug('__init__','controller={}'.format(controller))
        # The strip is it's own parent since the plugs are it's children
        #super(SmartStripNode, self).__init__(self, address, address, name)
        super().__init__(controller, controller.address, address, name)
        self.controller = controller

    def start(self):
        pass

    def shortPoll(self):
        try:
            if (self.dev.state == 'ON'):
                self.setDriver('ST',100)
            else:
                self.setDriver('ST',0)
        except:
            LOGGER.info('Short poll failed')

    def longPoll(self):
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
            LOGGER.info('Long poll failed')

    def set_on(self):
        self.dev.turn_on()
        self.setDriver('ST', 100)
        self.st = True

    def set_off(self):
        self.dev.turn_off()
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

    drivers = [{'driver': 'ST', 'value': 0, 'uom': 78},
                {'driver': 'CC', 'value': 0, 'uom': 1}, #amps
                {'driver': 'CV', 'value': 0, 'uom': 72}, #volts
                {'driver': 'CPW', 'value': 0, 'uom': 73}, #watts
                {'driver': 'TPW', 'value': 0, 'uom': 33}, #kWH
                {'driver': 'GV0', 'value': 0, 'uom': 2} #connection state
                ]
    id = 'SmartPlug'
    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
    }
