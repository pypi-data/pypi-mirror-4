'''
Created on 12-03-2013

@author: kamil
'''
import bisect

from PIL import Image

class BaseParser(object):
    
    LIMITS = [255]
    ICONS = " "
    
    def __init__(self, image, assume_sane=False):
        if not assume_sane:
            self._perform_sanity_tests()
        self.limits = self.__class__.LIMITS
        self.icons = self.__class__.ICONS
        self.image = self.process_image(image)
    
    def icon_for_pixel(self, pixel):
        """
        Inspect pixel and return matching character basing on whatever you
        wish.
        """
        raise NotImplementedError()
    
    def process_image(self, image):
        """
        If you know you need to transform image before all calls to parse
        (i.e. if you plan to process rgba image) this is the
        place to do it.
        """
        return image
    
    def process_icon(self, icon, pixel):
        """
        Modify the icon basing on pixel. This hook can be useful i.e. when
        generating html output. You can use it to wrap icons with colorful
        spans, or something. Default implementation is no-op.
        """
        return icon
    
    def process_row(self, row_string):
        """
        Default implementation just adds a newline at the end of row, but you may
        want to add `<br />` or do some other kind of fancy processing.
        """
        return row_string + "\n"
    
    def process_text(self, raw_result):
        """
        Default implementation is no-op but you can do some useful stuff here,
        like wrap the whole thing with `<html>` tags or something.
        """
        return raw_result
    
    def parse(self, width, height):
        """
        Let's roll! If you use hooks above you probably don't need to override this
        method.
        """
        img = self.image.resize((width, height), Image.ANTIALIAS)
        text = ""
        for y in range(0, img.size[1]):
            row = ""
            for x in range(0, img.size[0]):
                icon = self.icon_for_pixel(img.getpixel((x,y)))
                row += self.process_icon(icon, img.getpixel((x,y)))
            text += self.process_row(row)
        return self.process_text(text)
    
    def _perform_sanity_tests(self):
        limits = self.__class__.LIMITS
        icons = self.__class__.ICONS
        if len(limits) == 0 or len(icons) == 0: assert("`LIMITS` and `ICONS` should not be empty lists.")
        if len(limits) != len(icons): assert("`LIMITS` and `ICONS` should be equal length.")
        if limits[-1] != 255: assert("Last element of `LIMITS` should be 255")
        if sorted(limits) != limits: assert("Please use sorted (ascending) `LIMITS` list.")

class GreyscaleParser(BaseParser):
    
    ICONS = ' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'
    LIMITS = []
    
    def __init__(self, image, icons=None):
        super(GreyscaleParser, self).__init__(image, assume_sane=True)
        self.icons = icons if icons is not None else self.icons
        interval = 255/len(self.icons)
        limits = []
        for i in range(0,len(self.icons)):
            limits = [255-i*interval] + limits
        self.limits = limits
        
    def process_image(self, image):
        return image.convert("L")
    
    def icon_for_pixel(self, pixel):
        index=bisect.bisect_left(self.limits, 255-pixel)
        return self.icons[index]

class BinaryParser(GreyscaleParser):
    
    LIMITS = []
    ICONS = []
    
    def __init__(self, image, threshold=128, icons=" #"):
        super(BinaryParser, self).__init__(image, icons=icons)
        self.limits[0] = threshold

class HtmlGreyscaleParser(GreyscaleParser):
    
    def process_text(self, text):
        return '<pre>' + text + '<pre>'

class HtmlColorParser(HtmlGreyscaleParser):
    
    def process_image(self, image):
        return image.convert('RGB')
    
    def icon_for_pixel(self, pixel):
        index=bisect.bisect_left(self.limits, 255-(pixel[0]+pixel[1]+pixel[2])/3)
        return self.icons[index]
    
    def process_icon(self, icon, pixel):
        html_color = "#{0:02x}{1:02x}{2:02x}".format(*pixel)
        return '<span style="color: {0}">'.format(html_color) + icon + '</span>'
