""" Generic conversion utilities used by the Hue Node Server. """


def id_2_addr(hue_id):
    """ Convert a Phillips Hue ID to ISY Address """
    return hue_id.replace(':', '').replace('-', '')[-14:]


# Taken from: http://www.cse.unr.edu/~quiroz/inc/colortransforms.py
# License: Code is given as is. Use at your own risk and discretion.
# pylint: disable=invalid-name
def RGB_2_xy(R, G, B):
    """ Convert from RGB color to XY color. """
    if R + G + B == 0:
        return 0, 0

    var_R = (R / 255.)
    var_G = (G / 255.)
    var_B = (B / 255.)

    if var_R > 0.04045:
        var_R = ((var_R + 0.055) / 1.055) ** 2.4
    else:
        var_R /= 12.92

    if var_G > 0.04045:
        var_G = ((var_G + 0.055) / 1.055) ** 2.4
    else:
        var_G /= 12.92

    if var_B > 0.04045:
        var_B = ((var_B + 0.055) / 1.055) ** 2.4
    else:
        var_B /= 12.92

    var_R *= 100
    var_G *= 100
    var_B *= 100

    # Observer. = 2 deg, Illuminant = D65
    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

    # Convert XYZ to xy, see CIE 1931 color space on wikipedia
    return round(X / (X + Y + Z), 4), round(Y / (X + Y + Z), 4)


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


def color_xy(c_id):
    """ Lookup a color and return the XY values for that color. """
    return RGB_2_xy(*colors[c_id][1])


def bri2st(bri):
    return int(bri / 254. * 100.)

def st2bri(st):
    return round(st / 100. * 254., 4)

def kel2mired(value):
    if value != 0:
        return int(round(1e6 / value))
    else:
        return 0
