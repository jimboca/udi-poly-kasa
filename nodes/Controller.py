
import polyinterface
import logging,re,json,sys
from threading import Thread,Event
from node_funcs import get_valid_node_name
sys.path.insert(0,"pyHS100")
from pyHS100 import Discover
from nodes import SmartStripNode
from nodes import SmartPlugNode
from nodes import SmartBulbNode
LOGGER = polyinterface.LOGGER
logging.getLogger('pyHS100').setLevel(logging.DEBUG)

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
        LOGGER.info('Starting {}'.format(self.name))
        self.setDriver('ST', 1)
        self.server_data = self.poly.get_server_data(check_profile=True)
        LOGGER.info('{} Version {}'.format(self.name,self.server_data['version']))
        self.set_debug_level(self.getDriver('GV1'))
        self.heartbeat()
        self.check_params()
        self.discover()

    def shortPoll(self):
        if not self.discover_done:
            self.l_info('shortPoll','waiting for discover to complete')
            return
        if self.short_event is False:
            self.l_debug('shortPoll','Setting up Thread')
            self.short_event = Event()
            self.short_thread = Thread(name='shortPoll',target=self._shortPoll)
            self.short_thread.daemon = True
            self.l_debug('shortPoll','Starting Thread')
            st = self.short_thread.start()
            self.l_debug('shortPoll','Thread start st={}'.format(st))
        # Tell the thread to run
        self.l_debug('shortPoll','thread={} event={}'.format(self.short_thread,self.short_event),level=1)
        if self.short_event is not None:
            self.l_debug('shortPoll','calling event.set',level=1)
            self.short_event.set()
        else:
            self.l_error('shortPoll','event is gone? thread={} event={}'.format(self.short_thread,self.short_event))

    def _shortPoll(self):
        while (True):
            self.short_event.wait()
            self.l_debug('_shortPoll','start')
            for node in self.nodes:
                self.l_debug('shortPoll', 'node={} node.address={} self.address={}'.format(node,self.nodes[node].address,self.address),level=1)
                if self.nodes[node].address != self.address:
                    self.nodes[node].shortPoll()
            self.short_event.clear()
            self.l_debug('_shortPoll','done')

    def longPoll(self):
        self.heartbeat()
        if not self.discover_done:
            self.l_info('longPoll','waiting for discover to complete')
            return
        if self.long_event is False:
            self.l_debug('longPoll','Setting up Thread')
            self.long_event = Event()
            self.long_thread = Thread(name='longPoll',target=self._longPoll)
            self.long_thread.daemon = True
            self.l_debug('longPoll','Starting Thread')
            st = self.long_thread.start()
            self.l_debug('longPoll','Thread start st={}'.format(st))

    def _longPoll(self):
        while (True):
            self.short_event.wait()
            self.l_debug('_shortPoll','start')
            all_connected = True
            for node in self.nodes:
                if self.nodes[node].address != self.address:
                    try:
                        if self.nodes[node].is_connected():
                            self.nodes[node].longPoll()
                        else:
                            self.l_info('longPoll',"Known device not responding {} '{}'".format(self.nodes[node].address,self.nodes[node].name))
                            all_connected = False
                    except:
                        pass # in case node doesn't have a longPoll method
            if not all_connected:
                self.l_info("longPoll", "Not all devices are connected, running discover to check for them")
                self.discover_new()
            self.short_event.clear()
            self.l_debug('_shortPoll','done')

    def query(self):
        self.setDriver('ST', 1)
        self.reportDrivers()
        self.check_params()
        for node in self.nodes:
            if self.nodes[node].address != self.address:
                self.nodes[node].query()

    def heartbeat(self):
        self.l_debug('heartbeat','hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def discover(self):
        self.l_info('discover','start')
        devm = {}
        for dev in Discover.discover(target=self.poly.network_interface['broadcast']).values():
            self.l_debug('discover',"Got Device\n\tAlias:{}\n\tModel:{}\n\tMac:{}\n\tHost:{}".
                    format(dev.alias,dev.model,dev.mac,dev.host))
            #if self.add_node(cname,dev.mac,dev.host,dev.model,dev.alias):
            if self.add_node(dev=dev):
                devm[self.smac(dev.mac)] = True
        # make sure all we know about are added in case they didn't respond this time.
        for mac in self.polyConfig['customParams']:
            if not self.smac(mac) in devm:
                cfg = self.get_device_cfg(mac)
                if cfg is not None:
                    self.l_info('discover', "Adding previously known device that didn't respond to discover: {}".format(cfg))
                    self.add_node(cfg=cfg)
        self.discover_done = True
        LOGGER.info("discover: done")

    def discover_new(self):
        self.l_info('discover_new','start')
        for dev in Discover.discover(target=self.poly.network_interface['broadcast']).values():
            # Known Device?
            smac = self.smac(dev.mac)
            if smac in self.nodes_by_mac:
                # Make sure the host matches
                node = self.nodes_by_mac[smac]
                if dev.host != node.host:
                    self.l_warning('discover_new',"Updating '{}' host from {} to {}".format(node.name,node.host,dev.host))
                    node.host = dev.host
                    node.connect()
                else:
                    self.l_info('discover_new', "Connected:{} '{}'".format(node.is_connected(),node.name))
                    if not node.is_connected():
                        # Previously connected node
                        self.l_info('discover_new', "Connected:{} '{}' host is {} same as {}".format(node.is_connected(),node.name,node.host,dev.host))
                        node.connect()
            else:
                self.l_info('discover_new','found new device {}'.format(dev.alias))
                self.add_node(dev=dev)
        self.l_info("discover_new","done")

    # Add a node based on dev returned from discover or the stored config.
    def add_node(self, dev=None, cfg=None):
        if dev is not None:
            type =  dev.__class__.__name__
            mac  = dev.mac
            if type == 'SmartStrip':
                # String doesn't have an alias so use the mac
                name = 'SmartStrip {}'.format(mac)
            else:
                name = dev.alias
            cfg  = { "type": type, "name": name, "host": dev.host, "mac": mac, "model": dev.model, "address": get_valid_node_name(mac)}
        elif cfg is None:
            self.l_error("add_node","INTERNAL ERROR: dev={} and cfg={}".format(dev,cfg))
            return False
        self.l_info('discover',"adding {} '{}' {}".format(cfg['type'],cfg['name'],cfg['address']))
        #
        # Add Based on device type.  SmartStrip is a unique type, all others
        # are handled by SmartDevice
        #
        if cfg['type'] == 'SmartStrip':
            node = self.addNode(SmartStripNode(self, cfg['address'], cfg['name'],  dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartPlug':
            node = self.addNode(SmartPlugNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        elif cfg['type'] == 'SmartBulb':
            node = self.addNode(SmartBulbNode(self, cfg['address'], cfg['name'], dev=dev, cfg=cfg))
        else:
            self.l_error('discover',"Device type not yet supported: {}".format(cfg['type']))
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
        self.l_debug('save_cfg','Saving config: {}'.format(cfg))
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
            self.l_error('get_device_cfg','failed to parse cfg={0} Error: {1}'.format(cfg,err))
            return None
        return cfgd

    def set_all_logs(self,level):
        LOGGER.setLevel(level)
        # TODO: Set Kasa query logger level
        #logging.getLogger('requests').setLevel(level)

    def set_debug_level(self,level):
        self.l_info('set_debug_level',level)
        if level is None:
            level = 20
        level = int(level)
        if level == 0:
            level = 20
        self.l_info('set_debug_level','Set GV1 to {}'.format(level))
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level == 10:
            self.set_all_logs(logging.DEBUG)
        elif level == 20:
            self.set_all_logs(logging.INFO)
        elif level == 30:
            self.set_all_logs(logging.WARNING)
        elif level == 40:
            self.set_all_logs(logging.ERROR)
        elif level == 50:
            self.set_all_logs(logging.CRITICAL)
        else:
            self.l_error("set_debug_level","Unknown level {}".format(level))

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        pass

    def update_profile(self):
        self.l_info('update_profile','start')
        st = self.poly.installprofile()
        return st

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        self.l_info("cmd_set_debug_mode",val)
        self.set_debug_level(val)

    def _cmd_update_profile(self,command):
        self.update_profile()

    def _cmd_discover(self,cmd):
        self.discover_new()

    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))

    def l_error(self, name, string, exc_info=False):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))

    def l_debug(self, name, string, level=0, exc_info=False):
        if level <= self.debug_level:
            LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

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
