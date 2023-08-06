from PIL import ImageFont

colors = [
    '#edd400',   # butter 2
    '#73d216',   # chameleon 2
    '#fcaf3e',   # orange 1
    '#729fcf',   # sky blue 1
    '#ad7fa8',   # plum 1
    '#e9b96e',   # chocolate 1
    '#ef2929',   # scarlet red 1
    #'#d3d7cf',   # aluminium 2
    '#c4a000',   # butter 3
    '#4e9a06',   # chameleon 3
    '#f57900',   # orange 2
    '#3465a4',   # sky blue 2
    '#75507b',   # plum 2
    '#c17d11',   # chocolate 2
    '#a40000',   # scarlet red 3
    '#888a85',   # aluminium 4
]


def right_arrow_path(x, y, offset):
    """ x,y is the final point
    """
    d = [('m', x - 2 * offset, y),
        (offset, 0),
        (0, -offset),
        (offset, offset),
        (-offset, offset),
        (0, -offset),
        ('z')
    ]
    return d


def left_arrow_path(x, y, offset):
    """ x,y is the final point
    """
    d = [('m', x + 2 * offset, y),
        (-offset, 0),
        (0, offset),
        (-offset, -offset),
        (offset, -offset),
        (0, offset),
        ('z')
    ]
    return d


def top_arrow_path(x, y, offset):
    """ x,y is the final point
    """
    d = [('m', x, y + 2 * offset),
        (0, -offset),
        (-offset, 0),
        (offset, -offset),
        (offset, offset),
        (-offset, 0),
        ('z')
    ]
    return d


def bottom_arrow_path(x, y, offset):
    """ x,y is the final point
    """
    d = [('m', x, y - 2 * offset),
        (0, offset),
        (offset, 0),
        (-offset, offset),
        (-offset, -offset),
        (offset, 0),
        ('z')
    ]
    return d


class Point(tuple):
    mapper = dict(x=0, y=1)

    def __new__(cls, x, y):
        return super(Point, cls).__new__(cls, (x, y))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def shift(self, x=0, y=0):
        return self.__class__(self.x + x, self.y + y)


class Line(tuple):
    mapper = dict(x1=0, y1=1, x2=2, y2=3)

    def __new__(cls, x1, y1, x2, y2):
        return super(Line, cls).__new__(cls, (x1, y1, x2, y2))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def shift(self, x=0, y=0):
        return self.__class__(
            self.x1 + x, self.y1 + y, self.x2 + x, self.y2 + y)

    @property
    def start(self):
        return Point(self.x1, self.y1)

    @property
    def end(self):
        return Point(self.x2, self.y2)


class Size(tuple):
    mapper = dict(cx=0, cy=1)

    def __new__(cls, cx, cy):
        return super(Size, cls).__new__(cls, (cx, cy))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def shift(self, cx=0, cy=0):
        return self.__class__(self.cx + cx, self.cy + cy)

    def extend(self, cx=0, cy=0):
        return self.__class__(self.cx + cx, self.cy + cy)

    @property
    def width(self):
        return self.cx

    @property
    def height(self):
        return self.cy


class Box(list):
    mapper = dict(x=0, y=1, cx=2, cy=3)

    def __init__(self, x, y, cx, cy):
        super(Box, self).__init__((x, y, cx, cy))

    def __getattr__(self, name):
        return self[self.mapper[name]]

    def __repr__(self):
        class_name = self.__class__.__name__
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        addr = id(self)

        format = "<%(class_name)s (%(x)s, %(y)s) " + \
                 "%(width)dx%(height)d at 0x%(addr)08x>"
        return format % locals()

    def shift(self, x=0, y=0):
        return self.__class__(self.x + x, self.y + y,
                              self.cx, self.cy)

    def extend(self, cx=0, cy=0):
        return self.__class__(self.x, self.y,
                              self.cx + cx, self.cy + cy)

    @property
    def xy(self):
        return Point(self.x, self.y)

    @property
    def size(self):
        return Size(self.cx, self.cy)

    @property
    def width(self):
        return self.cx

    @property
    def height(self):
        return self.cy

    @property
    def topleft(self):
        return Point(self.x, self.y)

    @property
    def topright(self):
        return Point(self.x + self.cx, self.y)

    @property
    def bottomleft(self):
        return Point(self.x, self.y + self.cy)

    @property
    def bottomright(self):
        return Point(self.x + self.cx, self.y + self.cy)


def get_textsize(text, font_name, font_size):
    """ Return a tuple with
    """
    font = ImageFont.truetype(font_name, font_size)
    size = font.getsize(text)
    ascent, descent = font.getmetrics()
    return Size(size[0], size[1]), ascent, descent

