#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

#------------------------------------------------------------
#   Color manipulation
#------------------------------------------------------------

import math

def rgb2hsb(red, green, blue):
    """RGB to HSB color space conversion routine.
    red, green and blue are all numbers from 0 to 255.
    This routine returns three floating point numbers, hue, saturation, brightness.
    hue, saturation and brightness are all from 0.0 to 1.0.
    """
    c_min = min(red, green, blue)
    c_max = max(red, green, blue)

    if c_min == c_max:
        # Grayscale
        return 0.0, 0.0, float(c_max)
    elif red == c_min:
        d = green - blue
        h = 3.0
    elif green == c_min:
        d = blue - red
        h = 5.0
    else:
        d = red - green
        h = 1.0

    hue = (h - (float(d) / (c_max - c_min))) / 6.0
    saturation = (c_max - c_min) / float(c_max)
    brightness = c_max / 255.0

    return hue, saturation, brightness



def hsb2rgb(hue, saturation, brightness):
    """HSB to RGB color space conversion routine.
    hue, saturation and brightness are all from 0.0 to 1.0.
    This routine returns three integer numbers, red, green, blue.
    red, green and blue are all numbers from 0 to 255.
    """
    # Scale the brightness from a range of 0.0 thru 1.0
    #  to a range of 0.0 thru 255.0
    # Then truncate to an integer.
    brightness = int(min(brightness * 256.0, 255.0))
    #brightness = int(brightness * 255.0) # hG assumes this is correct
    
    if saturation == 0.0:
        # Grayscale because there is no saturation
        red = green = blue = brightness
    else:
        # Make hue angle be within a single rotation.
        # If the hue is > 1.0 or < 0.0, then it has
        #  "gone around the color wheel" too many times.
        #  For example, a value of 1.2 means that it has
        #  gone around the wheel 1.2 times, which is really
        #  the same ending angle as 0.2 trips around the wheel.
        # Scale it back to the 0.0 to 1.0 range.
        hue = hue - math.floor(hue)
        hue = hue * 6.0
        # Separate hue into int and fractional parts
        hue_i = int(hue)
        hue = hue - hue_i
        # Is hue even?
        if hue_i % 2 == 0:
            hue = 1.0 - hue
        #
        p = brightness * (1.0 - saturation)
        q = brightness * (1.0 - saturation * f)
        
        if hue_i == 1:
            red, green, blue = q, brightness, p
        elif hue_i == 2:
            red, green, blue = p, brightness, q
        elif hue_i == 3:
            red, green, blue = p, q, brightness
        elif hue_i == 4:
            red, green, blue = q, p, brightness
        elif hue_i == 5:
            red, green, blue = brightness, p, q
        else:
            red, green, blue = brightness, q, p
   
    return red, green, blue



def rgb(red, green, blue):
    """Return an integer which represents a color.
    The color is specified in RGB notation.
    Each of red, green and blue must be a number from 0 to 255.
    """
    return (int(red) & 255) << 16 | (int(green) & 255) << 8 | (int(blue) & 255)


def hsb(hue, saturation, brightness):
    """Return an integer which represents a color.
    The color is specified in HSB notation.
    Each of hue, saturation and brightness must be a number from 0.0 to 1.0.
    """
    return rgb(hsb2rgb(hue, saturation, brightness))


def red(color):
    """Return the Red component of a color as an integer from 0 to 255.
    color is an integer representing a color.
    This function is complimentary to the rgbColor function.
    """
    return (int(color) >> 16) & 255


def green(color):
    """Return the Green component of a color as an integer from 0 to 255.
    color is an integer representing a color.
    This function is complimentary to the rgbColor function.
    """
    return (int(color) >> 8) & 255


def blue(color):
    """Return the Blue component of a color as an integer from 0 to 255.
    color is an integer representing a color.
    This function is complimentary to the rgbColor function.
    """
    return int(color) & 255
