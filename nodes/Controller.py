
import polyinterface
import logging
from pyHS100 import Discover
from nodes import SmartStripNode

LOGGER = polyinterface.LOGGER
logging.getLogger('pyHS100').setLevel(logging.DEBUG)

class Controller(polyinterface.Controller):

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'TP-Link Kasa Controller'

    def start(self):
        LOGGER.info('Started TP-Link Kasa NodeServer')
        self.check_params()
        self.discover()

    def shortPoll(self):
        pass

    def longPoll(self):
        pass

    def query(self):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self):
        LOGGER.info("discover: start")
        for dev in Discover.discover().values():
            LOGGER.debug("discover: Got Device Mac:{} dev: {}".format(dev.mac,dev))
            cname = dev.__class__.__name__
            LOGGER.debug("discover: Device: {}".format(cname))
            if cname == 'SmartStrip':
                self.addNode(SmartStripNode(self, self.address, 'tplkaddress', 'TPLinkKasa Node Name'))
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

    id = 'controller'
    commands = {
      'QUERY': query,
      'DISCOVER': discover,
      'UPDATE_PROFILE': update_profile,
    }
    drivers = [
    {
      'driver': 'ST', 'value': 0, 'uom': 2
    }]
