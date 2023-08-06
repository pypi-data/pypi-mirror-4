# -*- encoding: utf-8 -*-
""" Convert a smachine into a layout of rectangles, lines, etc.

Sizes:
       Web       Desktop
       ------    -------
0.8em  ^= 13px
0.813em = 13px
0.875em = 14px
0.938em = 15px = 11pt
1em     = 16px = 12pt
1.063em = 17px = 13pt used by me in desktop
1.5em   = 24px

Lower letter no please, I'm too old.

Do I write the smachines with normal or reduced letter?
Right now, I think it's better work with normal letter. Again, I'm too old.
And there will always be time to change (or not?).

I choose for work with normal web apps:
    - 1em for normal letter,
    - 0.8em for a little reduced letter.

For blogs (more readability):
    - 1.063em for normal letter.

I choose for work with desktop apps:
    - 13pt for normal letter (1.063em, as blogs).

"""

from svgwrite.container import Group
import svgwrite.shapes
import svgwrite.text
import svgwrite.path
import svgwrite.animate

from ginsfsm.compat import iteritems_
from .utils import (
    get_textsize,
    Point, Size,
    colors,
    right_arrow_path,
    top_arrow_path,
    left_arrow_path,
    bottom_arrow_path,
    )
from .metrics import Metrics


class State(Group):
    """ Draw a state.

                             STATE rect

                        ----------------------
                       |  TITLE rect          | . . Event ONLY-OUT points
                       |----------------------|
    ACTION-IN points . |  ACTION rect         | . ACTION-OUT points
                     . |  ACTION rect         | .
                       |   .....              |
                     . |  ACTION rect         | .
                        ----------------------

    Everything needed to graphically represent a state.
    Requires only:
        - the names, the only variable data,
          also needed to calculate the width of the box;
          the maximum name length will be the width
          of the box, plus strokes, margins, etc (fixed data: metrics).
    """
    def __init__(self, layer, statedesc, stateid):
        """ statedesc and stateid are the state names/ids description.
        """
        super(State, self).__init__()
        self.layer = layer
        self.statedesc = statedesc
        self.stateid = stateid
        self.name = statedesc.name
        self.testing = False
        self.maximum_text_width = 0
        self.maximum_text_height = 0
        self.origin = Point(0, 0)
        self.state_rect = None
        self.blur_rect = None
        self.input_points = {}
        self.output_points = {}
        self.build_state_rect()

    def translate(self, x, y):
        self.origin = Point(x, y)
        super(State, self).translate(x, y)

    def resize(self, cx=None, cy=None):
        if cx is not None:
            self.state_rect.attribs['width'] = cx
            self.blur_rect.attribs['width'] = cx
            self.sep_line.commands[0][1][0] = cx
            for name, values  in iteritems_(self.output_points):
                output_point, connector, next_state = values
                output_point.x = cx - 2  # rectangle has a width of fixed 4.
                connector.attribs['x'] = cx - 2

        if cy is not None:
            self.state_rect.attribs['height'] = cy
            self.blur_rect.attribs['height'] = cy

    @property
    def size(self):
        return Size(self.state_rect.attribs['width'],
                    self.state_rect.attribs['height'])

    def build_state_rect(self):
        y = 0
        x_margin = self.layer.metrics.x_margin
        y_margin = self.layer.metrics.y_margin
        internal_size = self.get_maximum_text_element_size()
        external_size = internal_size.extend(x_margin * 2, y_margin)

        if 1:  # transparent_blur:
            filtr = "filter:url(#filter_blur);opacity:0.7;fill-opacity:1"
        else:
            filtr = "filter:url(#filter_blur)"

        self.blur_rect = svgwrite.shapes.Rect(
            Point(0, 0),
            Size(external_size.width, 0),
            rx=10,
            ry=10,
            fill='black',
            stroke='black',
            stroke_width=1,
            style=filtr,
        )
        self.add(self.blur_rect)

        self.state_rect = svgwrite.shapes.Rect(
            Point(0, 0),
            Size(external_size.width, 0),
            rx=10,
            ry=10,
            stroke='black',
            stroke_width=1,
            fill='#faf1e8')
        self.add(self.state_rect)

        if self.testing:
            title_rect = svgwrite.shapes.Rect(
                Point(x_margin, y_margin),
                internal_size,
                stroke='black',
                stroke_width=0.1,
                fill='white')
            self.add(title_rect)

        title_text = svgwrite.text.Text(self.statedesc.name,
            insert=Point(x_margin, y_margin + self.layer.metrics.ascent))
        self.add(title_text)

        y += external_size.height
        self.state_rect.attribs['height'] += external_size.height

        # separator line
        d = [('m', 0, y + y_margin / 2), [external_size.width, 0]]
        self.sep_line = svgwrite.path.Path(d=d, stroke='black', stroke_width=1)
        self.add(self.sep_line)

        for id in list(range(len(self.statedesc.ev_names))):
            ac_name = self.statedesc.ac_names[id]
            ev_name = self.statedesc.ev_names[id]
            next_state = self.statedesc.next_st_names[id]
            if self.testing:
                action_rect = svgwrite.shapes.Rect(
                    Point(x_margin, y + y_margin),
                    internal_size,
                    stroke='black',
                    stroke_width='0.2',
                    fill='white')
                self.add(action_rect)
            action_text = svgwrite.text.Text(ac_name,
                insert=Point(x_margin,
                             y + y_margin + self.layer.metrics.ascent))
            self.add(action_text)

            #
            #   Input point of the action (event)
            #
            input_point = Point(0, y + internal_size.height)
            self.input_points[ev_name] = input_point

            # draw a --. arrow with circle end.
            self.add(svgwrite.shapes.Line(
                input_point,
                input_point.shift(x_margin / 2),
                fill='black',
                stroke='black',
                stroke_width=1)
            )
            self.add(svgwrite.shapes.Circle(
                input_point.shift(x_margin / 2),
                r=3,
                fill='black',
                stroke='black',
                stroke_width=1)
            )

            #
            #   Output point of the action (next-state)
            #
            output_point = Point(external_size.width, y + internal_size.height)

            # draw a small square
            connector = self.add(svgwrite.shapes.Rect(
                output_point.shift(x=-2),
                (4, 4),
                fill='black',
                stroke='black',
                stroke_width=1)
            )
            # We use the ev_name because
            # the action_name and next_state can be None!.
            self.output_points[ev_name] = (output_point, connector, next_state)

            #
            #   Increment y-pointer and global state height
            #
            y += external_size.height
            self.state_rect.attribs['height'] += external_size.height

        self.state_rect.attribs['height'] += y_margin
        self.blur_rect.attribs['height'] = self.state_rect.attribs['height']

    def get_maximum_text_element_size(self):
        """ Calculate the greater element svgwrite.text area,
            including title and actions boxes
        """
        #print "%d-%s" % (stateid.id, statedesc.name)
        (width, height), ascent, descent = get_textsize(
                self.statedesc.name,
                self.layer.font_name,
                self.layer.font_size)
        self.maximum_text_width = max(self.maximum_text_width, width)
        self.maximum_text_height = max(self.maximum_text_height, height)

        for id in list(range(len(self.statedesc.ev_names))):
            # print "    ev: %d-%s -> ac: %s -> st: %d-%s" % (
            #    stateid.ev_ids[id],
            #    statedesc.ev_names[id],
            #    statedesc.ac_names[id],
            #    stateid.next_st_ids[id],
            #    statedesc.next_st_names[id],
            #)
            name = self.statedesc.ac_names[id]
            if name is None:
                continue
            (width, height), ascent, descent = get_textsize(
                name,
                self.layer.font_name,
                self.layer.font_size)
            self.maximum_text_width = max(self.maximum_text_width, width)
            self.maximum_text_height = max(self.maximum_text_height, height)
        return Size(self.maximum_text_width, self.maximum_text_height)


class StateDesc(object):
    """
    StateDesc: describe a state, his name, and three lists with the names of:
        - event name
        - action name
        - next state name
    The same index targets the same level or row of the three lists,
    in order to full the event/action/next-state trio.
    """
    def __init__(self, name, ev_names, ac_names, next_st_names):
        self.name = name
        self.ev_names = ev_names
        self.ac_names = ac_names
        self.next_st_names = next_st_names


class StateId(object):
    """
    StateId: describe the same as StateDesc, but with indexes instead of names.
    The indexes of states and events, could be better certainly
    the 'id'-entifiers, because they are uniques.
    """
    def __init__(self, id, ev_ids, next_st_ids):
        self.id = id
        self.ev_ids = ev_ids
        self.next_st_ids = next_st_ids


class States(Group):
    def __init__(self, layer, smachine):
        super(States, self).__init__()
        self.layer = layer
        self.states = []
        self.origin = Point(0, 0)
        self.smachine = smachine
        self.cx, self.cy = self.build_states()

    def build_states(self):
        """ Build the group of states.
            Return the size of group.
        """
        y = 0
        for idx, state_name in enumerate(self.smachine._state_list):
            if idx > 0:
                y += self.layer.metrics.states_y_margin

            st_id = self.smachine._state_index[state_name]
            state = self.smachine._states[st_id]
            event_name_list = []
            action_name_list = []
            next_state_name_list = []
            for ev_id, ev_ac in enumerate(state):
                if not isinstance(ev_ac, list):
                    continue
                action = ev_ac[0]
                if action is None:
                    action_name = ''
                else:
                    action_name = action.__name__
                next_state_id = ev_ac[1]
                if next_state_id is None:
                    next_state_name = ''
                else:
                    next_state_name = \
                        self.smachine._state_list[next_state_id - 1]

                event_name_list.append(self.smachine._event_list[ev_id - 1])
                action_name_list.append(action_name)
                next_state_name_list.append(next_state_name)

            statedesc = StateDesc(
                state_name,
                event_name_list,
                action_name_list,
                next_state_name_list)

            stateid = StateId(
                self.smachine._state_index[state_name],
                [self.smachine._event_index[event_name] \
                    for event_name in event_name_list],
                [self.smachine._state_index[state_name] \
                    for state_name in next_state_name_list]
            )

            state = State(self.layer, statedesc, stateid)
            state.translate(0, y)

            self.add(state)
            self.states.append(state)

            y += state.size.height

        # set all boxes and sep_line with the same width
        max_cx = 0
        for state in self.states:
            cx, cy = state.size
            max_cx = max(max_cx, cx)
        for state in self.states:
            state.resize(cx=max_cx)

        return (max_cx, y)

    def translate(self, x, y):
        self.origin = Point(x, y)
        super(States, self).translate(x, y)

    def get_input_points(self, event_name):
        points = []
        for state in self.states:
            point = state.input_points.get(event_name, None)
            if point:
                point = point.shift(state.origin.x - 1, state.origin.y)
                point = point.shift(self.origin.x - 1, self.origin.y)
                points.append(point)
        return points

    def get_output_points(self, event_name, states_filter=None):
        points = []
        for state in self.states:
            if states_filter and not state.name in states_filter:
                continue
            truplo = state.output_points.get(event_name, None)
            if truplo:
                # this output event is too an input event
                point, connector, next_state = truplo
                point = Point(connector.attribs['x'], connector.attribs['y'])
                point = point.shift(state.origin.x, state.origin.y)
                point = point.shift(self.origin.x, self.origin.y)
                point = point.shift(4, 2)
                points.append(point)
            else:
                # this is only a output event.
                # it's orphan, I don't know who action is broadcasting them.
                # TODO: analize the function source code and search
                # the output-events: broadcast, post_event, send_event
                pass

        return points

    def get_next_state_points(self):
        points = []
        for state in self.states:
            for name, values  in iteritems_(state.output_points):
                output_point, connector, next_state = values
                if not next_state:
                    continue
                point = Point(connector.attribs['x'], connector.attribs['y'])
                point = point.shift(state.origin.x, state.origin.y)
                point = point.shift(self.origin.x, self.origin.y)
                point = point.shift(4, 2)
                point_next_state = self.get_state_point(next_state)
                points.append((point, point_next_state))
        return points

    def get_state_point(self, state_name):
        for state in self.states:
            if state.name == state_name:
                return state.origin.shift(
                    self.origin.x + self.cx,
                    self.origin.y + self.layer.metrics.ascent
                )

    @property
    def size(self):
        return Size(self.cx, self.cy)


class InputEventLine(Group):
    def __init__(self, layer, name, start_point, end_points, color, level):
        super(InputEventLine, self).__init__(
            fill='none',
            stroke=color,
            stroke_width=layer.metrics.event_line_width,
            class_=name,
        )
        self.layer = layer
        self.name = name
        self.level = level
        self.start_point = start_point
        self.end_points = end_points
        self.build()
        highlight = svgwrite.animate.Set(
            attributeName='opacity',
            to='0.5',
            begin='mouseover',
            end='mouseout',
        )
        self.add(highlight)

    def add_right_arrow(self, points_list, end_point, size):
        points_list.append((end_point.x, end_point.y))
        points_list.append((end_point.x - size, end_point.y - size))
        points_list.append((end_point.x - size, end_point.y + size))
        points_list.append((end_point.x, end_point.y))

    def line_rect(self, start, end, level):
        r = 20
        d = [('M', start.x, start.y)]
        if level == 'top':
            d.append(('L', start.x, end.y - r))  # middle point
            d.append(('Q', start.x, end.y, start.x + r, end.y))
            d.append(('L', end.x, end.y))
        else:
            d.append(('L', start.x, end.y + r))  # middle point
            d.append(('Q', start.x, end.y, start.x + r, end.y))
            d.append(('L', end.x, end.y))
        line = svgwrite.path.Path(d=d)
        self.add(line)
        right_arrow = svgwrite.path.Path(d=right_arrow_path(end.x, end.y, 4))
        self.add(right_arrow)

    def build(self):
        for end_point in self.end_points:
            self.line_rect(self.start_point, end_point, self.level)


class OutputEventLine(Group):
    def __init__(self, layer, name, start_points, end_point, color, level):
        super(OutputEventLine, self).__init__(
            fill='none',
            stroke=color,
            stroke_width=layer.metrics.event_line_width,
            class_=name,
        )
        self.layer = layer
        self.name = name
        self.level = level
        self.start_points = start_points
        self.end_point = end_point
        self.build()
        highlight = svgwrite.animate.Set(
            attributeName='opacity',
            to='0.5',
            begin='mouseover',
            end='mouseout',
        )
        self.add(highlight)

    def add_top_arrow(self, points_list, end_point, size):
        points_list.append((end_point.x, end_point.y))
        points_list.append((end_point.x - size, end_point.y + size))
        points_list.append((end_point.x + size, end_point.y + size))
        points_list.append((end_point.x, end_point.y))

    def add_bottom_arrow(self, points_list, end_point, size):
        points_list.append((end_point.x, end_point.y))
        points_list.append((end_point.x + size, end_point.y - size))
        points_list.append((end_point.x - size, end_point.y - size))
        points_list.append((end_point.x, end_point.y))

    def line_rect(self, start, end, level):
        r = 20
        d = [('M', start.x, start.y)]
        if level == 'top':
            if start.x != end.x:
                d.append(('L', end.x - r, start.y))  # middle point
                d.append(('Q', end.x, start.y, end.x, start.y - r))
            d.append(('L', end.x, end.y))
        else:
            if start.x != end.x:
                d.append(('L', end.x - r, start.y))  # middle point
                d.append(('Q', end.x, start.y, end.x, start.y + r))
            d.append(('L', end.x, end.y))
        line = svgwrite.path.Path(d=d)
        self.add(line)

        if level == 'top':
            arrow = svgwrite.path.Path(d=top_arrow_path(end.x, end.y, 4))
        else:
            arrow = svgwrite.path.Path(d=bottom_arrow_path(end.x, end.y, 4))

        self.add(arrow)

    def build(self):
        for start_point in self.start_points:
            self.line_rect(start_point, self.end_point, self.level)


class StateChangeCurve(Group):
    def __init__(self, layer, name, start_point, end_point, axis, color):
        super(StateChangeCurve, self).__init__(
            fill='none',
            stroke=color,
            stroke_width=layer.metrics.state_change_line_width,
        )
        self.layer = layer
        self.name = name
        self.start_point = start_point
        self.end_point = end_point
        self.axis = axis
        self.build()
        highlight = svgwrite.animate.Set(
            attributeName='opacity',
            to='0.5',
            begin='mouseover',
            end='mouseout',
        )
        self.add(highlight)

    def build(self):
        self.line_curve(self.start_point, self.end_point, self.axis)

    def line_curve(self, start, end, axis):
        r = 10
        d = [('M', start.x, start.y)]
        if end.y > start.y:
            # to down
            d.append(('L', axis - r, start.y))
            d.append(('Q', axis, start.y, axis, start.y + r))
            d.append(('L', axis, end.y - r))
            d.append(('Q', axis, end.y, axis - r, end.y))
            d.append(('L', end.x, end.y))
        else:
            # to up
            d.append(('L', axis - r, start.y))
            d.append(('Q', axis, start.y, axis, start.y - r))
            d.append(('L', axis, end.y + r))
            d.append(('Q', axis, end.y, axis - r, end.y))
            d.append(('L', end.x, end.y))
        line = svgwrite.path.Path(d=d)
        self.add(line)

        arrow = svgwrite.path.Path(
            d=left_arrow_path(end.x, end.y, 8),
            fill='black',
        )

        self.add(arrow)


class Layer(Group):
    """
        Three zones: event zone, state zone and new-state zone:

          ev-zone   st-zone       ns-zone
        +---------+--------------+---------+
        |                                  |
        |           event names            |
        |                                  |
        +---------+--------------+---------+ -> tt_axis
        ||--------+--------------+--------||
        ||        |              |        ||
        ||        |   sep zone   |        ||
        ||        |              |        ||
        +---------+--------------+---------+ -> t_axis
        ||        |              |        ||
        ||        |              |        ||
        ||        |              |        ||
        ||        |   states     |        ||
        ||        |              |        ||
        ||        |              |        ||
        ||        |              |        ||
        +---------+--------------+---------+ -> b_axis
        ||        |              |        ||
        ||        |   sep zone   |        ||
        ||        |              |        ||
        ||--------|--------------|--------||
        +---------+--------------+---------+ -> bb_axis
        |                                  |
        |            event names           |
        |                                  |
        +---------+--------------+---------+
                  |              ^ r_axis
                  ^ l_axis

    """
    def __init__(self, smachine, font_name, font_size):
        super(Layer, self).__init__(font_family="DejaVu Sans",
                                    font_size=font_size)
        self.font_name = font_name
        self.font_size = font_size
        self.smachine = smachine
        self.metrics = Metrics(font_name, font_size)
        self.colors = {}

        #
        #   Build states
        #
        states = States(self, smachine)
        states_cx, states_cy = states.size

        top_input_events = smachine.get_top_input_events()
        top_output_events = smachine.get_top_output_events()
        bottom_input_events = smachine.get_bottom_input_events()
        bottom_output_events = smachine.get_bottom_output_events()
        state_changes = len(states.get_next_state_points()) + 1

        top_margin = self.metrics.top_margin
        bottom_margin = self.metrics.bottom_margin
        left_margin = self.metrics.left_margin
        right_margin = self.metrics.right_margin
        ev_line_sep = self.metrics.ev_line_sep
        st_line_sep = self.metrics.st_line_sep

        # let top space for top event_names
        if len(top_input_events) or len(top_output_events):
            self.tt_axis = self.metrics.tt_axis
        else:
            self.tt_axis = 20
        self.tt_axis += top_margin

        self.t_axis = self.metrics.t_axis
        self.t_axis += self.tt_axis

        # let left-right space for top/bottom input event lines
        self.l_axis = len(top_input_events) * ev_line_sep + \
                        len(bottom_input_events) * ev_line_sep + \
                        ev_line_sep + left_margin
        self.r_axis = self.l_axis + states_cx
        states.translate(self.l_axis, self.t_axis)

        # let left-right space for top/bottom output event lines
        self.cx = self.l_axis + \
                    states_cx + \
                    len(top_output_events) * ev_line_sep + \
                    len(bottom_output_events) * ev_line_sep + \
                    state_changes * st_line_sep + \
                    ev_line_sep + right_margin

        # let bottom space for bottom event_names
        self.b_axis = states_cy
        self.b_axis += self.t_axis
        self.bb_axis = self.metrics.bb_axis
        self.bb_axis += self.b_axis

        # extend height

        if len(bottom_input_events) or len(bottom_output_events):
            self.cy = self.bb_axis + self.metrics.tt_axis + bottom_margin
        else:
            self.cy = self.bb_axis + bottom_margin

        # assign color to events
        events = self.smachine.get_event_list()
        for idx, ev_name in enumerate(events):
            self.colors[ev_name] = colors[idx]

        # draw smachine rectangle
        smachine_rect = svgwrite.shapes.Rect(
            insert=(left_margin, self.tt_axis),
            size=(self.cx - left_margin - right_margin,
                  self.bb_axis - self.tt_axis),
            rx=10,
            ry=10,
            fill='#f8f8f8',
            stroke='#888a85',
            stroke_width=2,
        )
        self.add(smachine_rect)

        # draw states
        self.add(states)

        # draw smachine name
        self.add(svgwrite.text.Text(
            smachine.name,
            insert=(self.l_axis, top_margin),
            font_size=font_size * 2,
        ))

        # draw top input event lines
        gidx = 1
        for idx, ev_name in enumerate(top_input_events):
            start_point = Point(
                gidx * ev_line_sep + left_margin,
                self.tt_axis - 20
            )
            end_points = states.get_input_points(ev_name)
            line = InputEventLine(
                self,
                ev_name,
                start_point,
                end_points,
                self.colors[ev_name],
                level='top')
            self.add(line)

            text = svgwrite.text.Text(
                ev_name,
                insert=start_point.shift(0, -4),
            )
            text.rotate(-45, start_point)
            self.add(text)
            gidx += 1

        # draw bottom input event lines
        for idx, ev_name in enumerate(bottom_input_events):
            #drawing.defs.add(drawing.style('stylesheet-content'))

            start_point = Point(
                gidx * ev_line_sep + left_margin,
                self.bb_axis + 20
            )
            end_points = states.get_input_points(ev_name)
            line = InputEventLine(
                self,
                ev_name,
                start_point,
                end_points,
                self.colors[ev_name],
                level='bottom')
            self.add(line)

            text = svgwrite.text.Text(
                ev_name,
                insert=start_point.shift(0, self.metrics.ascent),
            )
            text.rotate(45, start_point)
            self.add(text)
            gidx += 1

        # draw top output event lines
        gidx = 1
        for idx, ev_name in enumerate(top_output_events):
            end_point = Point(
                gidx * ev_line_sep + self.r_axis + state_changes * st_line_sep,
                self.tt_axis - 20
            )
            states_filter = smachine.get_top_output_event_states(ev_name)
            start_points = states.get_output_points(ev_name, states_filter)
            if not start_points:
                # only output event
                start_points = [end_point.shift(0, 40)]
            line = OutputEventLine(
                self,
                ev_name,
                start_points,
                end_point,
                self.colors[ev_name],
                level='top')
            self.add(line)

            text = svgwrite.text.Text(
                ev_name,
                insert=end_point.shift(2, -4),
            )
            text.rotate(-45, end_point)
            self.add(text)
            gidx += 1

        # draw bottom output event lines
        for idx, ev_name in enumerate(bottom_output_events):
            end_point = Point(
                gidx * ev_line_sep + self.r_axis + state_changes * st_line_sep,
                self.bb_axis + 20
            )
            states_filter = smachine.get_bottom_output_event_states(ev_name)
            start_points = states.get_output_points(ev_name, states_filter)
            if not start_points:
                # only output event
                start_points = [end_point.shift(0, -40)]
            line = OutputEventLine(
                self,
                ev_name,
                start_points,
                end_point,
                self.colors[ev_name],
                level='bottom')
            self.add(line)

            text = svgwrite.text.Text(
                ev_name,
                insert=end_point.shift(4, 8),
            )
            text.rotate(45, end_point)
            self.add(text)
            gidx += 1

        # draw state changes
        gidx = 2
        state_change_start_end_points = states.get_next_state_points()
        for start_end in state_change_start_end_points:
            line = StateChangeCurve(
                self,
                ev_name,
                start_end[0],
                start_end[1],
                gidx * st_line_sep + self.r_axis,
                'black')
            self.add(line)
            gidx += 1

        # draw a general rectangle
        general_rect = svgwrite.shapes.Rect(
            Point(1, 1),
            Size(self.cx - 2, self.cy - 2),
            rx=10,
            ry=10,
            fill='none',
            stroke='#000000',
            stroke_opacity=1,
            stroke_width=1,
            stroke_miterlimit=4,
            stroke_dasharray=4.4,
            stroke_dashoffset=0.2,
        )
        self.add(general_rect)

    @property
    def size(self):
        return Size(self.cx, self.cy)

    @property
    def width(self):
        return self.cx

    @property
    def height(self):
        return self.cy
