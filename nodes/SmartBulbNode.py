#
# TP Link Kasa Smart Bulb Node
#
# This code is used for bulbs
#
import polyinterface,asyncio
from kasa import SmartBulb,SmartDeviceException
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
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            self.brightness = int(val)
            LOGGER.debug(f'{val}')
            self.setDriver('GV5',self.brightness)
            # This won't actually change unless the device is on
            asyncio.run(self.dev.set_brightness(int(bri2st(self.brightness))))
            asyncio.run(self.dev.update())
            self.setDriver('ST',self.dev.brightness)

    def brt(self):
        LOGGER.debug(f'{self.pfx} connected={self.connected}')
        asyncio.run(self.dev.update())
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness <= 255:
            self.set_bri(self.brightness + 15)

    def dim(self):
        LOGGER.debug('{self.pfx} connected={self.connected}')
        asyncio.run(self.dev.update())
        self.brightness = st2bri(self.dev.brightness)
        if self.is_connected() and self.brightness > 0:
            self.set_bri(self.brightness - 15)

    def set_hue(self,val):
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            asyncio.run(self.dev.update())
            hsv = list(self.dev.hsv)
            LOGGER.debug(f'{self.pfx} val={val}')
            hsv[0] = val
            self.dev.hsv = hsv
            asyncio.run(self.dev.set_hsv(hsv))
            self.setDriver('GV3',val)
            self.set_state()

    def set_sat(self,val):
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            asyncio.run(self.dev.update())
            hsv = list(self.dev.hsv)
            LOGGER.debug(f'{self.pfx} val={val}')
            hsv[1] = bri2st(val)
            self.dev.hsv = hsv
            asyncio.run(self.dev.set_hsv(hsv))
            self.setDriver('GV4',st2bri(val))
            self.set_state()

    def set_color_temp(self,val):
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            asyncio.run(self.dev.set_color_temp(int(val)))
            asyncio.run(self.dev.update())
            self.setDriver('CLITEMP',self.dev.color_temp)

    def set_color_name(self,val):
        LOGGER.debug(f'{self.pfx} connected={self.connected} val={val}')
        if self.is_connected():
            LOGGER.debug('set_color_name','rgb={}'.format(color_rgb(val)))
            asyncio.run(bulb.set_hsv(color_hsv(val)))
            self.set_state()

    def newdev(self):
        return SmartBulb(self.host)

    def cmd_set_on(self,command):
        asyncio.run(self.dev.turn_on())
        super().cmd_set_on(command)

    def cmd_set_off(self,command):
        asyncio.run(self.dev.turn_off())
        super().cmd_set_off(command)

    def cmd_set_bri(self,command):
        val = int(command.get('value'))
        LOGGER.info(f'{self.pfx} val={val}')
        asyncio.run(self.dev.turn_on())
        self.set_bri(val)

    def cmd_set_sat(self,command):
        val = int(command.get('value'))
        LOGGER.info(f'{self.pfx} val={val}')
        asyncio.run(self.dev.turn_on())
        self.set_sat(val)

    def cmd_set_hue(self,command):
        val = int(command.get('value'))
        LOGGER.info(f'{self.pfx} val={val}')
        asyncio.run(self.dev.turn_on())
        self.set_hue(val)

    def cmd_set_color_temp(self,command):
        asyncio.run(self.dev.turn_on())
        if not self.dev.is_variable_color_temp:
            LOGGER.error('{self.pfx} Not supported on this device?')
            return False
        val = int(command.get('value'))
        LOGGER.info(f'val={val}')
        self.set_color_temp(val)

    # TODO: Better to call get_list_state, set_light_state s
    def cmd_set_color_temp_brightness(self, command):
        if not self.dev.is_variable_color_temp:
            LOGGER.error('{self.pfx} Not supported on this device?')
            return False
        light_state = asyncio.run(self.dev.get_light_state())
        LOGGER.debug(f'{self.pfx} current_state={light_state}')
        #cstate = self.dev.get_light_state()
        query = command.get('query')
        #LOGGER.debug('cmd_set_color_temp_brightnesss','{}'.format(cstate))
        light_state['on_off'] = 1
        light_state['brightness'] = bri2st(int(query.get('BR.uom100')))
        ct = int(query.get('K.uom26'))
        if ct < self.dev.valid_temperature_range[0]:
            LOGGER.error(f'{self.pfx} color_temp={ct} is to low, using minimum {self.dev.valid_temperature_range[0]}')
            ct = self.dev.valid_temperature_range[0]
        elif ct > self.dev.valid_temperature_range[1]:
            LOGGER.error(f'{self.pfx} color_temp={ct} is to high, using maximum {self.dev.valid_temperature_range[1]}')
            ct = self.dev.valid_temperature_range[1]
        light_state['color_temp'] = ct

        LOGGER.debug(f'{self.pfx}     new_state={light_state}')
        try:
            asyncio.run(self.dev.set_light_state(light_state))
        except SmartDeviceException as ex:
            LOGGER.error(f'{self.pfx} failed: {ex}')
        self.set_state()

    def cmd_set_color_name(self,command):
        if not self.dev.is_color:
            LOGGER.error('{self.pfx} Not supported on this device')
        asyncio.run(self.dev.turn_on())
        val = int(command.get('value'))
        LOGGER.info(f'val={val}')
        self.set_color_name(val)

    def cmd_brt(self,command):
        if not self.dev.is_dimmable:
            LOGGER.error('{self.pfx} Not supported on this device')
        asyncio.run(self.dev.turn_on())
        self.brt()

    def cmd_dim(self,command):
        if not self.dev.is_dimmable:
            LOGGER.error('{self.pfx} Not supported on this device')
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
