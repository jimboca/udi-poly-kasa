
import polyinterface
import logging,re,json,sys,asyncio
from threading import Thread,Event
from node_funcs import get_valid_node_name
#sys.path.insert(0,"pyHS100")
#from pyHS100 import Discover
from kasa import Discover
from nodes import SmartStripNode
from nodes import SmartPlugNode
from nodes import SmartDimmerNode
from nodes import SmartBulbNode
from nodes import SmartLightStripNode
LOGGER = polyinterface.LOGGER
#logging.getLogger('pyHS100').setLevel(logging.DEBUG)

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Kasa Controller'
        self.address = 'tplkasactl'
        self.primary = self.address
        self.debug_level = 0 # TODO: More levels to add pyHS100 debugging (see discover.py)
        self.hb = 0
        self.nodes_by_mac = {}
        self.discover_done = False
        # For the short/long poll threads, we run them in threads so the main
        # process is always available for controlling devices
        self.short_event = False
        self.long_event  = False

    def start(self):
        LOGGER.info(f'Starting {self.name}')
        self.setDriver('ST', 1)
        self.server_data = self.poly.get_server_data(check_profile=True)
        LOGGER.info(f"{self.name} Version {self.server_data['version']}")
        self.set_debug_level(self.getDriver('GV1'))
        self.heartbeat()
        self.check_params()
        self.discover()

    def shortPoll(self):
        if not self.discover_done:
            LOGGER.info('waiting for discover to complete')
            return
        if self.short_event is False:
            LOGGER.debug('Setting up Thread')
            self.short_event = Event()
            self.short_thread = Thread(name='shortPoll',target=self._shortPoll)
            self.short_thread.daemon = True
            LOGGER.debug('Starting Thread')
            st = self.short_thread.start()
            LOGGER.debug(f'Thread start st={st}')
        # Tell the thread to run
        LOGGER.debug(f'thread={self.short_thread} event={self.short_event}')
        if self.short_event is not None:
            LOGGER.debug('calling event.set')
            self.short_event.set()
        else:
            LOGGER.error(f'event is gone? thread={self.short_thread} event={self.short_event}')

    def _shortPoll(self):
        while (True):
            self.short_event.wait()
            LOGGER.debug('start')
            for node in self.nodes:
                LOGGER.debug(f'node={node} node.address={self.nodes[node]} self.address={self.address}')
                if self.nodes[node].address != self.address:
                    self.nodes[node].shortPoll()
            self.short_event.clear()
            LOGGER.debug('done')

    def longPoll(self):
        self.heartbeat()
        if not self.discover_done:
            LOGGER.info('waiting for discover to complete')
            return
        if self.long_event is False:
            LOGGER.debug('Setting up Thread')
            self.long_event = Event()
            self.long_thread = Thread(name='longPoll',target=self._longPoll)
            self.long_thread.daemon = True
            LOGGER.debug('Starting Thread')
            st = self.long_thread.start()
            LOGGER.debug('Thread start st={st}')
        # Tell the thread to run
        LOGGER.debug(f'thread={self.long_thread} event={self.long_event}')
        if self.long_event is not None:
            LOGGER.debug('calling event.set')
            self.long_event.set()
        else:
            LOGGER.error(f'event is gone? thread={self.long_thread} event={self.long_event}')

    def _longPoll(self):
        while (True):
            self.long_event.wait()
            LOGGER.debug('start')
            all_connected = True
            for node in self.nodes:
                if self.nodes[node].address != self.address:
                    try:
                        if self.nodes[node].is_connected():
                            self.nodes[node].longPoll()
                        else:
                            LOGGER.warning(f"Known device not responding {self.nodes[node].address} '{self.nodes[node].name}'")
                            all_connected = False
                    except:
                        pass # in case node doesn't have a longPoll method
            if not all_connected:
                LOGGER.warning("Not all devices are connected, running discover to check for them")
                self.discover_new()
            self.long_event.clear()
            LOGGER.debug('done')

    def query(self):
        self.setDriver('ST', 1)
        self.reportDrivers()
        self.check_params()
        for node in self.nodes:
            if self.nodes[node].address != self.address:
                self.nodes[node].query()

    def heartbeat(self):
        LOGGER.debug('hb={self.hb}')
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    async def discover_add_device(self,dev):
        LOGGER.debug(f"{dev}")
        await dev.update()
        LOGGER.info(f"Got Device\n\tAlias:{dev.alias}\n\tModel:{dev.model}\n\tMac:{dev.mac}\n\tHost:{dev.host}")
        self.add_node(dev=dev)
        # Add to our list of added devices
        self.devm[self.smac(dev.mac)] = True

    def discover(self):
        LOGGER.info(f"start: {self.poly.network_interface['broadcast']} timout=10 discovery_packets=10")
        self.devm = {}
        devices = asyncio.run(Discover.discover(timeout=10,discovery_packets=10,target=self.poly.network_interface['broadcast'],on_discovered=self.discover_add_device))
        # make sure all we know about are added in case they didn't respond this time.
        for mac in self.polyConfig['customParams']:
            if not self.smac(mac) in self.devm:
                cfg = self.get_device_cfg(mac)
                if cfg is not None:
                    LOGGER.warning(f"Adding previously known device that didn't respond to discover: {cfg}")
                    self.add_node(cfg=cfg)
        self.discover_done = True
        LOGGER.info("done")

    async def discover_new_add_device(self,dev):
        # Known Device?
        await dev.update()
        smac = self.smac(dev.mac)
        if smac in self.nodes_by_mac:
            # Make sure the host matches
            node = self.nodes_by_mac[smac]
            if dev.host != node.host:
                LOGGER.warning(f"Updating '{node.name}' host from {node.host} to {dev.host}")
                node.host = dev.host
                node.connect()
            else:
                LOGGER.info(f"Connected:{node.is_connected()} '{node.name}'")
                if not node.is_connected():
                    # Previously connected node
                    LOGGER.warning("Connected:{node.is_connected()} '{node.name}' host is {node.host} same as {dev.host}")
                    node.connect()
        else:
            LOGGER.info(f'found new device {dev.alias}')
            self.add_node(dev=dev)

    def discover_new(self):
        LOGGER.info('start')
        devices = asyncio.run(Discover.discover(target=self.poly.network_interface['broadcast'],on_discovered=self.discover_new_add_device))
        LOGGER.info("done")

    # Add a node based on dev returned from discover or the stored config.
    def add_node(self, dev=None, cfg=None):
        if dev is not None:
            mac  = dev.mac
            if dev.is_bulb:
                type = 'SmartBulb'
                name = dev.alias
            elif dev.is_strip:
                type = 'SmartStrip'
                # SmartStrip doesn't have an alias so use the mac
                name = 'SmartStrip {}'.format(mac)
            elif dev.is_plug:
                type = 'SmartPlug'
                name = dev.alias
            elif dev.is_light_strip:
                type = 'SmartLightStrip'
                name = dev.alias
            elif dev.is_dimmable:
                type = 'SmartDimmer'
                name = dev.alias
            else:
                LOGGER.error(f"What is this? {dev}")
                return False
            LOGGER.info(f"Got a {type}")
            cfg  = { "type": type, "name": name, "host": dev.host, "mac": mac, "model": dev.model, "address": get_valid_node_name(mac)}
        elif cfg is None:
            LOGGER.error(f"INTERNAL ERROR: dev={dev} and cfg={cfg}")
            return False
        LOGGER.info(f"adding {cfg['type']} '{cfg['name']}' {cfg['address']}")
        #
        # Add Based on device type.  SmartStrip is a unique type, all others
        # are handled by SmartDevice
        #
#         LOGGER.error(f"alb:controller.py:{cfg['type']}")
        if cfg['type'] == 'SmartStrip':
            node = self.addNode(SmartStripNode(self, cfg['address'], cfg['name'],  dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartPlug':
            node = self.addNode(SmartPlugNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartDimmer':
            node = self.addNode(SmartDimmerNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartBulb':
            node = self.addNode(SmartBulbNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartLightStrip':
            node = self.addNode(SmartLightStripNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        else:
            LOGGER.error(f"Device type not yet supported: {cfg['type']}")
            return False
        # We always add it to update the host if necessary
        self.nodes_by_mac[self.smac(cfg['mac'])] = node
        return True

    def smac(self,mac):
        return re.sub(r'[:]+', '', mac)

    def exist_device_param(self,mac):
        cparams = self.polyConfig['customParams']
        return True if self.smac(mac) in cparams else False

    def save_cfg(self,cfg):
        LOGGER.debug(f'Saving config: {cfg}')
        js = json.dumps(cfg)
        cparams = self.polyConfig['customParams']
        cparams[self.smac(cfg['mac'])] = js
        self.addCustomParam(cparams)

    def get_device_cfg(self,mac):
        cfg = self.polyConfig['customParams'][self.smac(mac)]
        try:
            cfgd = json.loads(cfg)
        except:
            err = sys.exc_info()[0]
            LOGGER.error(f'failed to parse cfg={cfg} Error: {err}')
            return None
        return cfgd

    def set_all_logs(self,level):
        LOGGER.setLevel(level)
        # TODO: Set Kasa query logger level
        #logging.getLogger('requests').setLevel(level)

    def set_debug_level(self,level):
        LOGGER.info(f'level={level}')
        if level is None:
            level = 20
        level = int(level)
        if level == 0:
            level = 20
        LOGGER.info(f'Seting GV1 to {level}')
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        slevel = logging.WARNING
        if level <= 10:
            self.set_all_logs(logging.DEBUG)
            if level < 10:
                slevel = logging.DEBUG
        elif level == 20:
            self.set_all_logs(logging.INFO)
        elif level == 30:
            self.set_all_logs(logging.WARNING)
        elif level == 40:
            self.set_all_logs(logging.ERROR)
        elif level == 50:
            self.set_all_logs(logging.CRITICAL)
        else:
            LOGGER.error(f"Unknown level {level}")
        polyinterface.LOG_HANDLER.set_basic_config(True,slevel)

    def delete(self):
        LOGGER.info('Oh No I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        pass

    def update_profile(self):
        LOGGER.info('start')
        st = self.poly.installprofile()
        return st

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.info(f"val={val}")
        self.set_debug_level(val)

    def _cmd_update_profile(self,command):
        self.update_profile()

    def _cmd_discover(self,cmd):
        self.discover_new()

    id = 'KasaController'
    commands = {
      'SET_DM': cmd_set_debug_mode,
      'QUERY': query,
      'DISCOVER': _cmd_discover,
      'UPDATE_PROFILE': _cmd_update_profile,
    }
    drivers = [
        {'driver': 'ST',  'value':  1, 'uom':  2} ,
        {'driver': 'GV1', 'value': 30, 'uom': 25}, # Debug (Log) Mode, default=30 Warning
    ]
