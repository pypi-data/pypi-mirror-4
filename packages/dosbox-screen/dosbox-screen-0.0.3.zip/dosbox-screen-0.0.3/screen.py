# -*- coding: utf-8 -*-

"""Provides :class:`Screen`, which lets you write text to specific coordinates
   in the dos command shell, with colors.
"""
# pylint:disable=R0201,R0902
# R0201: method could be a function
# R0902: too many instance attributes

import sys
import struct
from ctypes import windll, create_string_buffer
import colorama
colorama.init()


class Screen(object):
    """Screen provides a interface for writing to the screen in the dosbox.
    """
    def __init__(self):
        s = self.__get_screen_info()
        self.buffer_width = s[0]
        self.buffer_height = s[1]
        self.buffer_x = s[2]
        self.buffer_y = s[3]
        self.buffer_left = s[5]
        self.buffer_top = s[6]
        self.buffer_right = s[7]
        self.buffer_bottom = s[8]
        self.maxx = s[9]
        self.maxy = s[10]

        self.xpos = self.buffer_x - self.buffer_left + 1
        self.ypos = self.buffer_y - self.buffer_top + 1

    @property
    def left(self):
        """The first column of the screen (the visible part of the screen
           buffer).
        """
        return 1

    @property
    def top(self):
        """The first row of the screen.
        """
        return 1

    @property
    def right(self):
        """The rightmost column of the screen.
        """
        return self.width + 1

    @property
    def bottom(self):
        """The last (bottom-most) row of the screen.
        """
        return self.height + 1

    @property
    def center(self):
        """The horizontal center of the screen.
        """
        return self.left + self.width // 2

    @property
    def middle(self):
        """The vertical middle of the screen.
        """
        return self.top + self.height // 2

    @property
    def width(self):
        """The width of the visible portion of the screen buffer.
        """
        return self.buffer_right - self.buffer_left + 1

    @property
    def height(self):
        """The height of the visible portion of the screen buffer.
        """
        return self.buffer_bottom - self.buffer_top + 1

    def __get_screen_info(self):
        """Call windows internals to get dimensions of dosbox.
        """
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if not res:
            raise RuntimeError("Error calling: GetConsoleScreenBufferInfo.")
        return struct.unpack("hhhhHhhhhhh", csbi.raw)

    def __repr__(self):
        import pprint
        return pprint.pformat(self.__dict__)

    def _xy(self, x, y):
        "Position the cursor at x, y."
        return '\033[%d;%dH' % (y, x)

    def gotoxy(self, x, y):
        """Put cursor at coordinates ``x``, ``y``.
        """
        sys.stdout.write(self._xy(x, y) + '')
        self.ypos = y
        self.xpos = x

    def write(self, *args, **kw):
        """Write args at current location, see writexy function for keyword
           arguments.
        """
        self.writexy(self.xpos, self.ypos, *args, **kw)

    def writexy(self, x, y, *args, **kw):
        """Write args at position x, y.
           Specify foreground and backround colors with keyword arguments.
           Available colors: black, red, green, yellow, blue, magenta, cyan
                             white, reset.
        """
        txt = ' '.join(str(a) for a in args)
        background = foreground = ''
        if 'foreground' in kw:
            foreground = getattr(colorama.Fore, kw['foreground'].upper())
        if 'background' in kw:
            background = getattr(colorama.Back, kw['background'].upper())
        cmd = self._xy(x, y)
        cmd += foreground
        cmd += background
        cmd += txt
        cmd += colorama.Style.RESET_ALL  # pylint:disable=E1101
        sys.stdout.write(cmd)
        self.ypos = y
        self.xpos = x + len(txt)

    def rightxy(self, x, y, *args, **kw):
        """Write text right justified at coordinates x, y.
        """
        txt = ' '.join(str(a) for a in args)
        self.writexy(x - len(txt), y, txt, **kw)

    def fill(self, x, y, width, height, char=' ', **kw):  # pylint:disable=R0913
        "Fill rectangle with char."
        for ypos in range(y, y + height):
            self.writexy(x, ypos, char * width, **kw)

    def cls(self, color=None):
        "Clear screen, fill it with the given color."
        args = {}
        if color:
            args['background'] = color
        self.fill(1, 1, self.width, self.height, char=' ', **args)
