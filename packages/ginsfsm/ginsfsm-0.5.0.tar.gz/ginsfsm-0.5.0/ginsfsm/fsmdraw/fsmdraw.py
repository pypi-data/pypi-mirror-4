# -*- encoding: utf-8 -*-
""" Draw a SMachine using svg format.
"""
import svgwrite
from .layout import Layer
import svgwrite.mixins


class FsmDraw(object):
    """ Draw a SMachine using svg format.
    """
    def __init__(self, smachine, filepath, font_name, font_size):
        self.smachine = smachine
        self.filepath = filepath
        self.font_name = font_name
        self.font_size = font_size
        self.drawer = None

    def draw(self):
        layout = Layer(self.smachine, self.font_name, self.font_size)
        self.render(layout)

    def pagesize(self):
        return self.size

    def save(self, size=None):
        """ save to file
        """
        #----------------------------#
        #   Save and convert to png
        #----------------------------#
        self.drawer.save()
        #data = open(self.filepath).read()
        #svg2png(data, self.filepath + '.png')

    def render(self, layout):
        """ Render the layout to svg
        """
        #--------------------------#
        #   Init drawing
        #--------------------------#
        self.size = layout.size
        self.drawer = drawer = svgwrite.Drawing(
            filename=self.filepath,
            profile='tiny',
            size=self.size,
            debug=False,
        )
        drawer.set_desc(title="", desc="Graph of a FSM")

        #
        #   Add filter_blur to use with all state's node boxes.
        #
        drawer['xmlns:inkspace'] = 'http://www.inkscape.org/namespaces/inkscape'
        # inkspace's Gaussian filter
        filtr = drawer.defs.add(
            drawer.filter(
                id='filter_blur',
                start=(-0.07875, -0.252),  # original -0.07875, -0.252
                size=(1.1575, 1.504),  # original 1.1575, 1.504
            )
        )
        filtr['inkspace:collect'] = 'always'
        gaussian = filtr.feGaussianBlur(
            id='feGaussianBlur3780',
            stdDeviation=4.2)
        gaussian['inkspace:collect'] = 'always'

        #--------------------------#
        #   Add layout
        #--------------------------#
        self.drawer.add(layout)
