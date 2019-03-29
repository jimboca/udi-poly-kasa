
import polyinterface
import logging
from node_funcs import get_valid_node_name
from pyHS100 import Discover
from nodes import SmartStripNode

LOGGER = polyinterface.LOGGER
logging.getLogger('pyHS100').setLevel(logging.DEBUG)

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'TP-Link Kasa Controller'
        self.address = 'tplkasactl'
        self.primary = self.address
        self.debug_level = 0 # TODO: More levels to add pyHS100 debugging (see discover.py)
        self.hb = 0

    def start(self):
        LOGGER.info('Started TP-Link Kasa NodeServer')
        self.setDriver('ST', 1)
        self.heartbeat()
        self.check_params()
        self.discover()

    def shortPoll(self):
        for node in self.nodes:
            self.l_debug('shortPoll', 'node={} node.address={} self.address={}'.format(node,self.nodes[node].address,self.address),level=1)
            if self.nodes[node].address != self.address:
                self.nodes[node].shortPoll()

    def longPoll(self):
        self.heartbeat()

    def query(self):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

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
        for dev in Discover.discover().values():
            self.l_debug('discover',"Got Device\n\tAlias:{}\n\tModel:{}\n\tMac:{}\n\tHost:{}".
                    format(dev.alias,dev.model,dev.mac,dev.host))
            cname = dev.__class__.__name__
            self.l_debug('discover','cname={}'.format(cname))
            if cname == 'SmartStrip':
                nname = get_valid_node_name(dev.mac)
                self.l_info('discover','adding SmartStrip {}'.format(nname))
                self.addNode(SmartStripNode(self, nname, 'SmartStrip {}'.format(dev.mac), dev))
            else:
                self.l_warning('discover',"Device not yet supported: {}".format(dev))
        LOGGER.info("discover: done")

    def delete(self):
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def check_params(self):
        pass

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def l_info(self, name, string):
        LOGGER.info("%s:%s:%s: %s" %  (self.id,self.name,name,string))

    def l_error(self, name, string, exc_info=False):
        LOGGER.error("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

    def l_warning(self, name, string):
        LOGGER.warning("%s:%s:%s: %s" % (self.id,self.name,name,string))

    def l_debug(self, name, string, level=0, exc_info=False):
        if level <= self.debug_level:
            LOGGER.debug("%s:%s:%s: %s" % (self.id,self.name,name,string), exc_info=exc_info)

    id = 'TPLinkKasaController'
    commands = {
      'QUERY': query,
      'DISCOVER': discover,
      'UPDATE_PROFILE': update_profile,
    }
    drivers = [
    {
      'driver': 'ST', 'value': 1, 'uom': 2
    }]
