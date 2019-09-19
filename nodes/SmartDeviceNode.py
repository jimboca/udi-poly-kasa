#
# TP Link Kasa Smart Device Node
# All Devices are one of these to share the common methods
#
#
import re
import polyinterface

LOGGER = polyinterface.LOGGER

class SmartDeviceNode(polyinterface.Node):

    def __init__(self, controller, parent_address, address, name, model, host):
        self.controller = controller
        self.name = name
        self.host = host
        self.debug_level = 0
        self.st = None
        self.id = re.sub(r'[\(\)]+', '', model)

        self.l_debug('__init__','controller={} address={} name={} host={}'.format(controller,address,name,host))
        super().__init__(controller, parent_address, address, name)

    def start(self):
        self.connect()
        self.set_state()

    def shortPoll(self):
        self.set_state()

    def longPoll(self):
        if not self.connected:
            self.l_info('longPoll', 'Not connected, will retry...')
            self.connect()

    def connect(self):
        self.l_debug('connect', '', level=0, exc_info=False)
        try:
            self.dev = self.newdev()
            self.l_info('connect', 'connected: {}'.format(self.dev))
            self.set_connected(True)
        except:
            self.l_error("start", "Unable to connect to device '{}' {} will try again later".format(self.name,self.host), exc_info=True)
            self.set_connected(False)
        return self.connected

    def set_on(self):
        self.dev.turn_on()
        self.set_state()

    def set_off(self):
        self.dev.turn_off()
        self.set_state()

    def set_state(self):
        if self.connected:
            try:
                if (self.dev.state == 'ON'):
                    self.setDriver('ST',100)
                else:
                    self.setDriver('ST',0)
            except:
                self.l_error('set_state','failed', exc_info=True)
        else:
            self.l_debug('set_state', "Not connected")

    def set_connected(self,st):
        self.l_debug('set_connected', "{}".format(st), level=0, exc_info=False)
        self.connected = st
        self.setDriver('GV1',1 if st else 0)

    def is_connected(self):
        return self.connected

    def query(self):
        self.set_state()
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
