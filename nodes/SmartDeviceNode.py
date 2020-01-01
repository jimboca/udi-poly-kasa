#
# TP Link Kasa Smart Device Node
# All Devices are one of these to share the common methods
#
#
import re
import polyinterface
from pyHS100 import SmartDeviceException
from converters import bri2st,st2bri
from threading import Thread,Event

LOGGER = polyinterface.LOGGER

class SmartDeviceNode(polyinterface.Node):

    def __init__(self, controller, parent_address, address, name, dev, cfg):
        self.controller = controller
        self.name = name
        self.dev  = dev
        self.cfg  = cfg
        self.l_debug('__init__','dev={}'.format(dev))
        self.l_debug('__init__','cfg={}'.format(cfg))
        self.host = cfg['host']
        self.debug_level = 0
        self.st = None
        self.event  = None
        self.connected = None # So start will force setting proper status
        self.l_debug('__init__','controller={} address={} name={} host={}'.format(controller,address,name,self.host))
        if cfg['emeter']:
            self.drivers.append({'driver': 'CC', 'value': 0, 'uom': 1}) #amps
            self.drivers.append({'driver': 'CV', 'value': 0, 'uom': 72}) #volts
            self.drivers.append({'driver': 'CPW', 'value': 0, 'uom': 73}) #watts
            self.drivers.append({'driver': 'TPW', 'value': 0, 'uom': 33}) #kWH
        self.cfg['id'] = self.id
        super().__init__(controller, parent_address, address, name)

    def start(self):
        self.l_debug('start','Setting up Threads')
        self.short_event = Event()
        self.short_thread = Thread(target=self._shortPoll)
        self.short_thread.daemon = True
        self.long_event = Event()
        self.long_thread = Thread(target=self._longPoll)
        self.long_thread.daemon = True
        self.l_debug('start','Starting Threads')
        st = self.short_thread.start()
        self.l_debug('start','Short Thread start st={}'.format(st))
        st = self.long_thread.start()
        self.l_debug('start','Long Thread start st={}'.format(st))

    def shortPoll(self):
        # Tells the thread to finish
        self.l_debug('shortPoll','thread={} event={}'.format(self.short_thread,self.short_event))
        if self.short_event is not None:
            self.l_debug('shortPoll','calling event.set')
            self.short_event.set()
        else:
            self.l_error('shortPoll','event is gone? thread={} event={}'.format(self.short_thread,self.short_event))

    def _shortPoll(self):
        if self.dev is not None:
            self.set_connected(True)
        else:
            self.set_connected(False)
        self.connect()
        self.set_state()
        while (True):
            self.l_debug('_shortPoll','waiting...')
            self.short_event.wait()
            self.l_debug('_shortPoll','running...')
            self.set_state()
            self.short_event.clear()

    def longPoll(self):
        # Tells the thread to finish
        self.l_debug('longPoll','thread={} event={}'.format(self.long_thread,self.long_event))
        if self.long_event is not None:
            self.l_debug('longPoll','calling event.set')
            self.long_event.set()
        else:
            self.l_error('longPoll','event is gone? thread={} event={}'.format(self.long_thread,self.long_event))

    def _longPoll(self):
        while (True):
            self.l_debug('_shortPoll','waiting...')
            self.short_event.wait()
            self.l_debug('_shortPoll','running...')
            if not self.connected:
                self.l_info('longPoll', 'Not connected, will retry...')
                self.connect()
            if self.connected:
                self.set_energy()
            self.short_event.clear()

    def set_energy(self):
        if self.cfg['emeter']:
            try:
                energy = self.dev.get_emeter_realtime()
                self.l_debug('set_energy','{}'.format(energy))
                if energy is not None:
                    # rounding the values reduces driver updating traffic for
                    # insignificant changes
                    if 'current' in energy:
                        self.setDriver('CC',round(energy['current'],3))
                    if 'voltage' in energy:
                        self.setDriver('CV',round(energy['voltage'],1))
                    if 'power' in energy:
                        self.setDriver('CPW',round(energy['power'],3))
                    elif 'power_mw' in energy:
                        self.setDriver('CPW',round(energy['power_mw']/1000,3))
                    if 'total' in energy:
                        self.setDriver('TPW',round(energy['total'],3))
            #trap SmartDeviceException here with simple error message
            except:
                self.l_error('set_energy','failed', exc_info=True)

    # Nothing by default
    def set_all_drivers(self):
        pass

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
        self.set_energy()

    def set_off(self):
        self.dev.turn_off()
        self.set_state()
        self.set_energy()

    def set_state(self):
        # We don't use self.connected here because dev might be good, but device is unplugged
        # So then when it's plugged back in the same dev will still work
        if self.dev is not None:
            try:
                if (self.dev.state == 'ON'):
                    if self.dev.is_dimmable:
                        self.setDriver('ST',self.dev.brightness)
                        self.setDriver('GV5',int(st2bri(self.dev.brightness)))
                    else:
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
            except Exception as ex:
                if self.connected:
                    self.l_error('set_state','failed', exc_info=True)
                    self.set_connected(False)
            # On restore, or initial startup, set all drivers.
            if self.connected:
                try:
                    self.set_all_drivers()
                except Exception as ex:
                    self.l_error('set_state','set_all_drivers failed: {}'.format(ex),exc_info=True)
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
