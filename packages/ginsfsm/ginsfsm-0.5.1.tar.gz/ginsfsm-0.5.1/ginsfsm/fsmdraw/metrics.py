# -*- encoding: utf-8 -*-

from .utils import get_textsize


class Metrics(object):
    def __init__(self, font_name, font_size):
        # Calculate state box metrics
        # box action zone
        self.font_name = font_name
        self.font_size = font_size
        self.calculate_metrics()

    def calculate_metrics(self):
        # use the A letter as base
        size, ascent, descent = get_textsize(
            "AA", self.font_name, self.font_size)

        # state title
        self.ascent = ascent
        self.descent = descent
        self.y_margin = size.height / 2
        self.x_margin = size.width * 1
        self.states_y_margin = 40

        self.state_change_line_width = 2
        self.event_line_width = 4
        self.tt_axis = 120
        self.t_axis = 50
        self.bb_axis = 50

        self.top_margin = 40
        self.bottom_margin = 30
        self.left_margin = 30
        self.right_margin = 60

        self.ev_line_sep = 25
        self.st_line_sep = 10
