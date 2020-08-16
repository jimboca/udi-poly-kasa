#
# TP Link Kasa Smart Device Node
# All Devices are one of these to share the common methods
#
#
import re,asyncio
import polyinterface
from kasa import SmartDeviceException
from converters import bri2st,st2bri

LOGGER = polyinterface.LOGGER

class SmartDeviceNode(polyinterface.Node):

    def __init__(self, controller, parent_address, address, name, dev, cfg):
        self.controller = controller
        self.name = name
        self.dev  = dev
        self.cfg  = cfg
        self.pfx = f"{self.name}:"
        LOGGER.debug(f'{self.pfx} dev={dev}')
        LOGGER.debug(f'{self.pfx} cfg={cfg}')
        self.ready = False
        self.host = cfg['host']
        self.debug_level = 0
        self.st = None
        self.event  = None
        self.connected = None # So start will force setting proper status
        LOGGER.debug(f'{self.pfx} controller={controller} address={address} name={name} host={self.host}')
        if cfg['emeter']:
            self.drivers.append({'driver': 'CC', 'value': 0, 'uom': 1}) #amps
            self.drivers.append({'driver': 'CV', 'value': 0, 'uom': 72}) #volts
            self.drivers.append({'driver': 'CPW', 'value': 0, 'uom': 73}) #watts
            self.drivers.append({'driver': 'TPW', 'value': 0, 'uom': 33}) #kWH
        self.cfg['id'] = self.id
        super().__init__(controller, parent_address, address, name)

    def start(self):
        self.connect()
        self.ready = True

    def query(self):
        self.set_state()
        self.set_energy()
        self.reportDrivers()

    def shortPoll(self):
        if not self.ready:
            return
        # Keep trying to connect if possible
        self.connect()
        self.set_state()

    def longPoll(self):
        if not self.connected:
            LOGGER.info(f'{self.pfx} Not connected, will retry...')
            self.connect()
        if self.connected:
            self.set_energy()

    def connect(self):
        if not self.is_connected():
            LOGGER.debug(f'{self.pfx} connected={self.is_connected()}')
            try:
                self.dev = self.newdev()
                # We can get a dev, but not really connected, so make sure we are connected.
                asyncio.run(self.dev.update())
                sys_info = self.dev.sys_info
                self.set_connected(True)
            except SmartDeviceException as ex:
                LOGGER.error(f"{self.pfx} Unable to connect to device '{self.name}' {self.host} will try again later: {ex}")
                self.set_connected(False)
            except:
                LOGGER.error(f"{self.pfx} Unknown excption connecting to device '{self.name}' {self.host} will try again later", exc_info=True)
                self.set_connected(False)
        return self.is_connected

    def set_on(self):
        asyncio.run(self.dev.turn_on())
        self.set_state()
        self.set_energy()

    def set_off(self):
        asyncio.run(self.dev.turn_off())
        self.set_state()
        self.set_energy()

    def set_state(self):
        # This doesn't call set_energy, since that is only called on long_poll's
        # We don't use self.connected here because dev might be good, but device is unplugged
        # So then when it's plugged back in the same dev will still work
        if self.dev is not None:
            try:
                asyncio.run(self.dev.update())
                if (self.dev.is_on):
                    if self.dev.is_dimmable:
                        self.setDriver('ST',self.dev.brightness)
                        self.setDriver('GV5',int(st2bri(self.dev.brightness)))
                    else:
                        self.setDriver('ST',100)
                else:
                    self.setDriver('ST',0)
                if not self.connected:
                    LOGGER.info(f'{self.pfx} Connection restored')
                    self.set_connected(True)
            except SmartDeviceException as ex:
                if self.connected:
                    LOGGER.error(f'{self.pfx} failed: {ex}')
                    self.set_connected(False)
            except Exception as ex:
                if self.connected:
                    LOGGER.error(f'{self.pfx} failed', exc_info=True)
                    self.set_connected(False)
            # On restore, or initial startup, set all drivers.
            if self.connected:
                try:
                    self.set_all_drivers()
                except Exception as ex:
                    LOGGER.error(f'{self.pfx} set_all_drivers failed: {ex}',exc_info=True)
        else:
            if self.connected:
                LOGGER.debug(f"{self.pfx} No device")
                self.set_connected(False)

    # Called by set_state when device is alive, does nothing by default
    def set_all_drivers(self):
        pass

    def set_energy(self):
        if self.cfg['emeter']:
            try:
                energy = self.dev.emeter_realtime
                LOGGER.debug(f'{self.pfx} {energy}')
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
            except SmartDeviceException as ex:
                LOGGER.error(f'{self.pfx} failed: {ex}')
            except:
                LOGGER.error(f'{self.pfx} failed', exc_info=True)
        else:
            LOGGER.debug(f'{self.pfx} no energy')

    def set_connected(self,st):
        # Just return if setting to same status
        if st == self.connected:
            return
        LOGGER.debug(f"{self.pfx} {st}")
        self.connected = st
        self.setDriver('GV0',1 if st else 0)
        if st:
            # Make sure current cfg is saved
            LOGGER.debug(f"{self.pfx} save_cfg {st}")
            try:
                self.cfg['host']  = self.dev.host
                self.cfg['model'] = self.dev.model
                self.controller.save_cfg(self.cfg)
            except SmartDeviceException as ex:
                LOGGER.error(f'{self.pfx} failed: {ex}')
            except:
                LOGGER.error(f'{self.pfx} unknown failure', exc_info=True)

    def is_connected(self):
        return self.connected

    def cmd_set_on(self, command):
        self.set_on()

    def cmd_set_off(self, command):
        self.set_off()
