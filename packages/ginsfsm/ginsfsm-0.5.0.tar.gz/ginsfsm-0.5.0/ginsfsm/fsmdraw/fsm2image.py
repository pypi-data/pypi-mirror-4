from ginsfsm.smachine import SMachine
from .fsmdraw import FsmDraw


def fsm2image(filepath, fsm, fsm_name, output_format,
              maxwidth=None,
              font_name='./DejaVuSans.ttf',
              font_size=14):
    """ Convert the fsm into a sphinx image.
    """
    smachine = SMachine(fsm)
    smachine.name = fsm_name

    # generate the svg file
    drawer = FsmDraw(smachine, filepath, font_name, font_size)
    drawer.draw()
    drawer.save()

    if output_format == 'png':
        # todo
        pass
    elif output_format == 'pdf':
        # todo
        pass

    """
    size = drawer.pagesize()
    if maxwidth and maxwidth < size[0]:
        ratio = float(maxwidth) / size[0]
        thumb_size = (maxwidth, size[1] * ratio)

        thumb_filepath = '_thumb' + filepath
        drawer.filename = thumb_filepath
        drawer.draw()
        drawer.save(thumb_size)

        image = nodes.image(uri=thumb_filepath, target=filepath)
    else:
        image = nodes.image(uri='/_static/' + filename + '.svg')
        #from ginsfsm.sphinxext import xxxmath
        #image = xxxmath(uri='../../images/' + filename + '.svg')
    """
