""" Generic conversion utilities used by the Hue Node Server. """

from colorsys import rgb_to_hsv

""" Common color names and their RGB values. """
colors = {
    0: ['aqua', [127, 255, 212]],
    1: ['azure', [0, 127, 255]],
    2: ['beige', [245, 245, 220]],
    3: ['blue', [0, 0, 255]],
    4: ['chartreuse', [127, 255, 0]],
    5: ['coral', [0, 63, 72]],
    6: ['crimson', [220, 20, 60]],
    7: ['forest green', [34, 139, 34]],
    8: ['fuchsia', [255, 119, 255]],
    9: ['golden', [255, 215, 0]],
    10: ['gray', [128, 128, 128]],
    11: ['green', [0, 255, 0]],
    12: ['hot pink', [252, 15, 192]],
    13: ['indigo', [75, 0, 130]],
    14: ['lavender', [181, 126, 220]],
    15: ['lime', [191, 255, 0]],
    16: ['maroon', [128, 0, 0]],
    17: ['navy blue', [0, 0, 128]],
    18: ['olive', [128, 128, 0]],
    19: ['red', [255, 0, 0]],
    20: ['royal blue', [8, 76, 158]],
    21: ['tan', [210, 180, 140]],
    22: ['teal', [0, 128, 128]],
    23: ['white', [255, 255, 255]]
 }

# From: http://code.activestate.com/recipes/576919-python-rgb-and-hsv-conversion/
# Easier to use than colorsys.rgb_to_hsv
def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = int((60 * ((g-b)/df) + 360) % 360)
    elif mx == g:
        h = int((60 * ((b-r)/df) + 120) % 360)
    elif mx == b:
        h = int((60 * ((r-g)/df) + 240) % 360)
    if mx == 0:
        s = 0
    else:
        s = int((df/mx) * 100)
    v = int(mx * 100)
    return h, s, v

def xcolor_hsv(c_id):
    """ Lookup a color and return the hsv values for that color. """
    c = colors[int(c_id)][1]
    if c[0] > 0:
        c[0] /= 255
    if c[1] > 0:
        c[1] /= 255
    if c[2] > 0:
        c[2] /= 255
    t = rgb_to_hsv(*c)
    return [bri2st(t[0]*255),bri2st(t[1]*255),bri2st(t[2]*255)]

def color_hsv(c_id):
    """ Lookup a color and return the hsv values for that color. """
    return rgb2hsv(*colors[int(c_id)][1])

def color_xy(c_id):
    """ Lookup a color and return the XY values for that color. """
    return RGB_2_xy(*colors[c_id][1])

def color_rgb(c_id):
    return colors[int(c_id)][1]

def bri2st(bri):
    return int(bri / 254. * 100.)

def st2bri(st):
    return int(st / 100. * 254)

def kel2mired(value):
    if value != 0:
        return int(round(1e6 / value))
    else:
        return 0
