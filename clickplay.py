#!/usr/bin/env python
import Quartz as Q
import ctypes
import ctypes.util
import array
from PIL import Image
import pytesseract
import numpy as np

def init_core_graphics():
    path = ctypes.util.find_library('CoreGraphics')
    ctypes.CDLL(path).CGSInitialize()

def get_window_rect(title):
    windows = Q.CGWindowListCopyWindowInfo(Q.kCGWindowListOptionOnScreenOnly, Q.kCGNullWindowID)
    for window in windows:
        if window.get('kCGWindowName') == title:
            bounds = window.get('kCGWindowBounds')
            origin = (bounds.get('X'), bounds.get('Y'))
            size = (bounds.get('Width'), bounds.get('Height'))
            return Q.CGRect(origin, size)
    raise RuntimeError('window not found')

def get_rect_display(rect):
    displays = array.array('I')
    displays.append(0)
    Q.CGGetDisplaysWithRect(rect, 1, displays, None)
    return displays[0]

def capture_screen(display, rect):
    image = Q.CGDisplayCreateImageForRect(display, rect)
    width = Q.CGImageGetWidth(image)
    height = Q.CGImageGetHeight(image)
    data = Q.CGDataProviderCopyData(Q.CGImageGetDataProvider(image))
    return Image.frombytes('RGBA', (width, height), data)

def ocr_capture(image):
    # Beware: coordinates are for a Retina display Mac
    fields = {
        # left, top, right, bottom
        'money': (270, 90, 870, 170),
        'level': (1400, 208, 2000, 254),
        'dps': (40, 300, 400, 340),
        'click_dmg': (40, 345, 400, 385),
        'hero_souls': (740, 300, 1100, 340),
        'ascend_souls': (740, 345, 1100, 385),
        'hero_1_name': (340, 455, 855, 500),
        'hero_1_dmg': (340, 500, 550, 550),
        'hero_1_lvl': (645, 500, 855, 550),
        'hero_2_name': (340, 669, 855, 714),
        'hero_2_dmg': (340, 714, 550, 764),
        'hero_2_lvl': (645, 714, 855, 764),
        'hero_3_name': (340, 883, 855, 928),
        'hero_3_dmg': (340, 928, 550, 978),
        'hero_3_lvl': (645, 928, 855, 978)
    }
    for label, box in fields.iteritems():
        subimage = image.crop(box)

        data = np.array(subimage)
        red, green, blue, alpha = data.T
        not_white_areas = (red < 240) | (green < 240) | (blue < 240)
        data[not_white_areas.T] = (0, 0, 0, 255)
        subimage = Image.fromarray(data)

        text = pytesseract.image_to_string(subimage)
        text = text.replace(' ', '')
        text = text.replace('.', ',')
        text = text.replace(r"L\I'|", 'Lvl') # This is some wacky nonsense

        print( label, text )
        #subimage.save('{}.png'.format(label))

def main():
    init_core_graphics()
    rect = get_window_rect('Clicker Heroes')
    display = get_rect_display(rect)
    image = capture_screen(display, rect)
    ocr_capture(image)

if __name__ == '__main__':
    main()
