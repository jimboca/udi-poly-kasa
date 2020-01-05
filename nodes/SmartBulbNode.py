#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface
from pyHS100 import SmartBulb
from nodes import SmartDeviceNode
from converters import RGB_2_xy, color_xy, bri2st, kel2mired

LOGGER = polyinterface.LOGGER

class SmartBulbNode(SmartDeviceNode):

    def __init__(self, controller, address, name, dev=None, cfg=None):
        self.name = name
        self.debug_level = 0
        self.drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 51},
            {'driver': 'GV0', 'value': 0, 'uom': 2},  #connection state
            {'driver': 'GV5', 'value': 0, 'uom': 100}, #brightness
        ]
        if dev is not None:
            # Figure out the id based in the device info
            self.id = 'SmartBulb_'
            if dev.is_dimmable:
                self.id += 'D'
            else:
                self.id += 'N'
            if dev.is_variable_color_temp:
                self.id += 'T'
            else:
                self.id += 'N'
            if dev.is_color:
                self.id += 'C'
            else:
                self.id += 'N'
            if dev.has_emeter:
                self.id += 'E'
            else:
                self.id += 'N'
            cfg['emeter'] = dev.has_emeter
            cfg['color']  = dev.is_color
            cfg['color_temp'] = dev.is_variable_color_temp
        else:
            self.id = cfg['id']
        if cfg['color_temp']:
            self.drivers.append({'driver': 'CLITEMP', 'value': 0, 'uom': 26})
        if cfg['color']:
            self.drivers.append({'driver': 'GV3', 'value': 0, 'uom': 100}) #hue
            self.drivers.append({'driver': 'GV4', 'value': 0, 'uom': 100}) #sat
        super().__init__(controller, controller.address, address, name, dev, cfg)

    def set_all_drivers(self):
        if self.dev.is_variable_color_temp:
            self.setDriver('CLITEMP',self.dev.color_temp)
        #is_variable_color_temp
        #if self.is_color:
        pass

    def set_bri(self,val):
        self.l_debug('set_bri','connected={} val={}'.format(self.connected,val))
        if self.connected:
            self.brightness = int(val)
            self.l_debug('set_bri','{}'.format(val))
            self.setDriver('GV5',self.brightness)
            # This won't actually change unless the device is on
            self.dev.brightness = int(bri2st(self.brightness))
            self.setDriver('ST',self.dev.brightness)

    def set_color_temp(self,val):
        self.l_debug('set_color_temp','connected={} val={}'.format(self.connected,val))
        if self.connected:
            self.dev.color_temp = int(val)
            self.setDriver('CLITEMP',self.dev.color_temp)

    def newdev(self):
        return SmartBulb(self.host)

    def cmd_set_on(self,command):
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        super().cmd_set_off(command)

    def cmd_set_bri(self,command):
        val = int(command.get('value'))
        self.l_info("cmd_set_bri",val)
        self.set_bri(val)

    def cmd_set_color_temp(self,command):
        if not self.dev.is_variable_color_temp:
            self.l_error('cmd_set_color_temp','Not supported on this device?')
            return False
        val = int(command.get('value'))
        self.l_info("cmd_set_color_temp",val)
        self.set_color_temp(val)

    # TODO: Better to call get_list_state, set_light_state s
    def cmd_set_color_temp_brightness(self, command):
        if not self.dev.is_variable_color_temp:
            self.l_error('cmd_set_color_temp_brightnesss','Not supported on this device?')
            return False
        #cstate = self.dev.get_light_state()
        query = command.get('query')
        #self.l_debug('cmd_set_color_temp_brightnesss','{}'.format(cstate))
        light_state = {
            "on_off": 1,
            "brightness": bri2st(int(query.get('BR.uom100'))),
            "color_temp": int(query.get('K.uom26')),
        }
        self.l_debug('cmd_set_color_temp_brightnesss','{}'.format(light_state))
        self.dev.set_light_state(light_state)


    def setColorRGB(self, command):
        if 'xy' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but RGB command is received".format(self.data['type'], self.data['name']))
            return False
        super().setColorRGB(command)

    def setColorXY(self, command):
        if 'xy' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but XY command is received".format(self.data['type'], self.data['name']))
            return False
        super().setColorXY(command)

    def setColor(self, command):
        if 'xy' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but Color command is received".format(self.data['type'], self.data['name']))
            return False
        super().setColor(command)

    def setHue(self, command):
        if 'hue' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but HUE command is received".format(self.data['type'], self.data['name']))
            return False
        super().setHue(command)

    def setSat(self, command):
        if 'sat' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but SAT command is received".format(self.data['type'], self.data['name']))
            return False
        super().setSat(command)

    def setColorHSB(self, command):
        if 'hue' not in self.data['action']:
            LOGGER.info("{} {} does not have Color lights but HSB command is received".format(self.data['type'], self.data['name']))
            return False
        super().setColorHSB(command)


    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
        'SET_BRI': cmd_set_bri,
        'CLITEMP' : cmd_set_color_temp,
        'SET_CTBR' : cmd_set_color_temp_brightness,
    }
