#
# TP Link Kasa Smart Device Node
# All Devices are one of these to share the common methods
#
#
import re
import polyinterface
from pyHS100 import SmartDeviceException

LOGGER = polyinterface.LOGGER

_known_devices = {
    'HS100US': True,
    'HS110US': True,
    'HS300US': True,
    'KL130US': True,
    'KL110US': True,
}

class SmartDeviceNode(polyinterface.Node):

    def __init__(self, controller, parent_address, address, name, dev, cfg):
        self.controller = controller
        self.name = name
        self.dev  = dev
        self.cfg  = cfg
        self.l_debug('__init__','dev={}'.format(dev))
        self.l_debug('__init__','cfg={}'.format(cfg))
        if dev is not None:
            self.host = dev.host
        else:
            self.host = cfg['host']
        self.debug_level = 0
        self.st = None
        self.connected = None # So start will force setting proper status
        sid =  re.sub(r'[\(\)]+', '', cfg['model'])
        if sid in _known_devices:
            self.id = sid
        else:
            self.id = self.default
            self.l_error('__init__',"Device '{}' is an uknown model {}, using {}".format(name,sid,self.id))
        self.l_debug('__init__','controller={} address={} name={} host={}'.format(controller,address,name,self.host))
        super().__init__(controller, parent_address, address, name)

    def start(self):
        if self.dev is not None:
            self.set_connected(True)
        else:
            self.set_connected(False)
        self.connect()
        self.set_state()

    def shortPoll(self):
        self.set_state()

    def longPoll(self):
        if not self.connected:
            self.l_info('longPoll', 'Not connected, will retry...')
            self.connect()

    def connect(self):
        self.l_debug('connect', 'connected={}'.format(self.is_connected()), level=0, exc_info=False)
        if not self.is_connected():
            try:
                self.dev = self.newdev()
                # We can get a dev, but not really connected, so make sure we are connected.
                sys_info = self.dev.sys_info
                self.set_connected(True)
            except SmartDeviceException as ex:
                if self.connected:
                    self.l_error("start", "Unable to connect to device '{}' {} will try again later".format(self.name,self.host), exc_info=False)
                self.set_connected(False)
            except:
                self.l_error("start", "Unknown excption connecting to device '{}' {} will try again later".format(self.name,self.host), exc_info=True)
                self.set_connected(False)
        return self.connected

    def set_on(self):
        self.dev.turn_on()
        self.set_state()

    def set_off(self):
        self.dev.turn_off()
        self.set_state()

    def set_state(self):
        # We don't use self.connected here because dev might be good, but device is unplugged
        # So then when it's plugged back in the same dev will still work
        if self.dev is not None:
            try:
                if (self.dev.state == 'ON'):
                    self.setDriver('ST',100)
                else:
                    self.setDriver('ST',0)
                if not self.connected:
                    self.l_info('set_state','Connection restored')
                    self.set_connected(True)
            except SmartDeviceException as ex:
                if self.connected:
                    self.l_error('set_state','failed: {}'.format(ex))
                    self.set_connected(False)
            except:
                if self.connected:
                    self.l_error('set_state','failed', exc_info=True)
                    self.set_connected(False)
        else:
            if self.connected:
                self.l_debug('set_state', "No device")
                self.set_connected(False)

    def set_connected(self,st):
        if st == self.connected:
            return
        self.l_debug('set_connected', "{}".format(st), level=0, exc_info=False)
        self.connected = st
        self.setDriver('GV0',1 if st else 0)
        if st:
            # Make sure current cfg is saved
            self.l_debug('set_connected', "save_cfg".format(st), level=0, exc_info=False)
            try:
                self.cfg['host'] = self.dev.host
                self.cfg['model'] = self.dev.model
                self.controller.save_cfg(self.cfg)
            except:
                self.l_error('set_connected','failed', exc_info=True)

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
