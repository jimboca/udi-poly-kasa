#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface
from pyHS100 import SmartBulb
from nodes import SmartDeviceNode
from converters import color_hsv, color_rgb, bri2st, st2bri

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
        if self.dev.is_dimmable:
            self.brightness = st2bri(self.dev.brightness)
        if self.dev.is_color:
            hsv = self.dev.hsv
            self.setDriver('GV3',hsv[0])
            self.setDriver('GV4',st2bri(hsv[1]))
            self.setDriver('GV5',st2bri(hsv[2]))
        if self.dev.is_variable_color_temp:
            self.setDriver('CLITEMP',self.dev.color_temp)

    def set_bri(self,val):
        self.l_debug('set_bri','connected={} val={}'.format(self.connected,val))
        if self.is_connected():
            self.brightness = int(val)
            self.l_debug('set_bri','{}'.format(val))
            self.setDriver('GV5',self.brightness)
            # This won't actually change unless the device is on
            self.dev.brightness = int(bri2st(self.brightness))
            self.setDriver('ST',self.dev.brightness)

    def brt(self):
        self.l_debug('bri','connected={}'.format(self.connected))
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness <= 255:
            self.set_bri(self.brightness + 15)

    def dim(self):
        self.l_debug('dim','connected={}'.format(self.connected))
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness > 0:
            self.set_bri(self.brightness - 15)

    def set_hue(self,val):
        self.l_debug('set_hue','connected={} val={}'.format(self.connected,val))
        if self.is_connected():
            hsv = list(self.dev.hsv)
            self.l_debug('set_hsv','{}'.format(val))
            hsv[0] = val
            self.dev.hsv = hsv
            self.setDriver('GV3',val)
            self.set_state()

    def set_sat(self,val):
        self.l_debug('set_sat','connected={} val={}'.format(self.connected,val))
        if self.is_connected():
            hsv = list(self.dev.hsv)
            self.l_debug('set_sat','{}'.format(val))
            hsv[1] = bri2st(val)
            self.dev.hsv = hsv
            self.setDriver('GV4',st2bri(val))
            self.set_state()

    def set_color_temp(self,val):
        self.l_debug('set_color_temp','connected={} val={}'.format(self.connected,val))
        if self.is_connected():
            self.dev.color_temp = int(val)
            self.setDriver('CLITEMP',self.dev.color_temp)

    def set_color_name(self,val):
        self.l_debug('set_color_name','connected={} val={}'.format(self.connected,val))
        if self.is_connected():
            self.l_debug('set_color_name','rgb={}'.format(color_rgb(val)))
            self.dev.hsv = color_hsv(val)
            self.set_state()

    def newdev(self):
        return SmartBulb(self.host)

    def cmd_set_on(self,command):
        self.dev.turn_on()
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        self.dev.turn_off()
        super().cmd_set_off(command)

    def cmd_set_bri(self,command):
        val = int(command.get('value'))
        self.l_info("cmd_set_bri",val)
        self.dev.turn_on()
        self.set_bri(val)

    def cmd_set_sat(self,command):
        val = int(command.get('value'))
        self.l_info("cmd_set_sat",val)
        self.dev.turn_on()
        self.set_sat(val)

    def cmd_set_hue(self,command):
        val = int(command.get('value'))
        self.l_info("cmd_set_hue",val)
        self.dev.turn_on()
        self.set_hue(val)

    def cmd_set_color_temp(self,command):
        self.dev.turn_on()
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
        # Must turn on before we adjust
        self.dev.turn_on()
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
        self.dev.set_state()

    def cmd_set_color_name(self,command):
        if not self.dev.is_color:
            self.l_error('cmd_set_color_name','Not supported on this device')
        self.dev.turn_on()
        self.set_color_name(command.get('value'))

    def cmd_brt(self,command):
        if not self.dev.is_dimmable:
            self.l_error('cmd_brt','Not supported on this device')
        self.dev.turn_on()
        self.brt()

    def cmd_dim(self,command):
        if not self.dev.is_dimmable:
            self.l_error('cmd_dim','Not supported on this device')
        self.dim()

    commands = {
        'DON': cmd_set_on,
        'DOF': cmd_set_off,
        'SET_BRI': cmd_set_bri,
        'SET_HUE': cmd_set_hue,
        'SET_SAT': cmd_set_sat,
        'CLITEMP' : cmd_set_color_temp,
        'SET_CTBR' : cmd_set_color_temp_brightness,
        'SET_COLOR' : cmd_set_color_name,
        'BRT': cmd_brt,
        'DIM': cmd_dim,
    }
