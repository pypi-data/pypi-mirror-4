# -*- coding: utf-8 -*-
"""
Sphinx extension that displays the API documentation:
    * a table with the :ref:`gobj` parameters.
    * a svg image representing the :ref:`smachine`.
"""
import posixpath
import os
from os import path
import re
import imp
from math import ceil

import docutils
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from ginsfsm.fsmdraw.fsm2image import fsm2image
from ginsfsm.compat import iteritems_


class smachinenode(nodes.General, nodes.Element):
    pass


class GinsFSMDirective(Directive):
    """
    Directive to insert arbitrary dot markup.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'fsm': directives.unchanged,
        'gconfig': directives.unchanged,
    }
    domain = 'py'

    def run(self):
        fsm_node = smachinenode()
        fsm = self.options['fsm']  # required
        fsm_node['fsm'] = fsm

        gconfig_node = []
        gconfig = self.options.get('gconfig')  # optional
        if gconfig:
            gconfig_node = [build_gconfig_node(self, gconfig)]
        return gconfig_node + [fsm_node]


def rst2node(data):
    """Converts a reStructuredText into its node
    """
    if not data:
        return
    parser = docutils.parsers.rst.Parser()
    document = docutils.utils.new_document('<>')
    document.settings = docutils.frontend.OptionParser().get_default_values()
    document.settings.tab_width = 4
    document.settings.pep_references = False
    document.settings.rfc_references = False
    parser.parse(data, document)
    if len(document.children) == 1:
        return document.children[0]
    else:
        par = docutils.nodes.paragraph()
        for child in document.children:
            par += child
        return par


def gene_paragraph(rawtext):
    """ Generate paragraph
    """
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
    return paragraph


def build_table(table_data, col_widths, col_rest,
                header_rows=1, stub_columns=0):
    """ build table
    """
    table = nodes.table()
    table.attributes['border'] = 1
    tgroup = nodes.tgroup(cols=len(col_widths))
    table += tgroup
    for col_width in col_widths:
        colspec = nodes.colspec(colwidth=col_width)
        if stub_columns:
            colspec.attributes['stub'] = 1
            stub_columns -= 1
        tgroup += colspec
    rows = []
    for row in table_data:
        row_node = nodes.row()
        for idx, cell in enumerate(row):
            entry = nodes.entry()
            if col_rest[idx]:
                n = rst2node(cell)
            else:
                n = None
            if isinstance(n, nodes.paragraph):
                entry += n
            else:
                entry += gene_paragraph(cell)
            row_node += entry
        rows.append(row_node)
    if header_rows:
        thead = nodes.thead()
        thead.extend(rows[:header_rows])
        tgroup += thead
    tbody = nodes.tbody()
    tbody.extend(rows[header_rows:])
    tgroup += tbody
    return table


def build_gconfig_node(self, gconfig_name):
    src = self.state.document.current_source.split(':')[0]
    gconfig_id = self.state.document.current_source.split(':')[1]
    gconfig_id = gconfig_id.split()[2]
    gconfig_id = gconfig_id + '.gconfig'
    module, ext = os.path.splitext(os.path.split(src)[-1])
    #TODO load_source is deprecated in python3.3.
    # It must be changed by load_module
    py_mod = imp.load_source(module, src)
    gconfig = getattr(py_mod, gconfig_name)

    gconfig_node = nodes.definition_list('', ids=[gconfig_id])

    rows = []
    rows.append(['Name', 'Type', 'Default value', 'Description'])
    for parameter_name, definition in iteritems_(gconfig):
        type_, default_value, flag, validate_function, desc = definition
        if type_ is None:
            type_ = 'None'
        else:
            type_ = type_.__name__
        type_ = "``%s``" % type_
        parameter_name = "``%s``" % parameter_name
        default_value = str(default_value)
        row = [parameter_name, type_, default_value, desc]
        rows.append(row)

    cols_len = [40, 20, 30, 100]
    cols_rest = [1, 1, 0, 1]
    table = build_table(rows, cols_len, cols_rest)

    title = "Configurable Parameters:"
    dl_item = nodes.definition_list_item(
        "",
        nodes.term("", "", nodes.emphasis(title, title)),
        nodes.definition("", table)
    )
    gconfig_node += dl_item

    return gconfig_node


def render_smachine(self, node, fsm_name, output_format):
    src = node.source.split(':')[0]
    module, ext = os.path.splitext(os.path.split(src)[-1])
    try:
        py_mod = imp.load_source(module, src)
    except:
        print('ERROR importing "%s" module from %s' % (module, src))
        raise
    fsm = getattr(py_mod, fsm_name)

    fname = '%s.%s' % (fsm_name, output_format)

    if hasattr(self.builder, 'imgpath'):
        # HTML
        relfn = posixpath.join(self.builder.imgpath, fname)
        outfn = path.join(self.builder.outdir, '_images', fname)
        imgdir = path.join(self.builder.outdir, '_images')
        try:
            os.makedirs(imgdir)
        except OSError:
            pass

    else:
        # LaTeX
        relfn = fname
        outfn = path.join(self.builder.outdir, fname)

    # TODO add title? fsm_node += nodes.title(text='Diagram:\n')

    # TODO: create and use the maxwidth option
    fsm2image(outfn, fsm, fsm_name, output_format)

    return relfn, outfn


svg_dim_re = re.compile(r'<svg\swidth="(\d+)pt"\sheight="(\d+)pt"', re.M)


def get_svg_tag(svgref, svgfile):
    # Webkit can't figure out svg dimensions when using object tag
    # so we need to get it from the svg file
    fp = open(svgfile, 'r')
    try:
        for line in fp:
            match = svg_dim_re.match(line)
            if match:
                dimensions = match.groups()
                break
        else:
            dimensions = None
    finally:
        fp.close()

    # We need this hack to make WebKit show our object tag properly
    def pt2px(x):
        return int(ceil((96.0 / 72.0) * float(x)))

    if dimensions:
        style = ' width="%s" height="%s"' % tuple(map(pt2px, dimensions))
    else:
        style = ''

    # The object tag works fine on Firefox and WebKit
    # Besides it's a hack, this strategy does not mess with templates.
    #return '<object type="image/svg+xml" data="%s"%s></object>\n' % \
    #       (svgref, style)
    return '<embed type="image/svg+xml" src="%s"%s/>\n' % \
           (svgref, style)


def render_smachine_html(self, node, smachine):
    fname, outfn = render_smachine(self, node, smachine, 'svg')

    self.body.append(self.starttag(node, 'dl', CLASS='smachine'))
    self.body.append('<dt><em>Diagram:</em></dt>')

    self.body.append('<dd>')
    svgtag = get_svg_tag(fname, outfn)
    self.body.append(svgtag)
    self.body.append('</dd>')

    self.body.append('</dl>\n')
    raise nodes.SkipNode


def html_visit_smachinenode(self, node):
    render_smachine_html(self, node, node['fsm'])


def render_smachine_latex(self, node, smachine):
    fname, outfn = render_smachine(self, smachine, 'pdf')
    inline = node.get('inline', False)
    if inline:
        para_separator = ''
    else:
        para_separator = '\n'

    if fname is not None:
        caption = node.get('caption')
        # XXX add ids from previous target node
        if caption and not inline:
            self.body.append('\n\\begin{figure}[h!]')
            self.body.append('\n\\begin{center}')
            self.body.append('\n\\caption{%s}' % self.encode(caption))
            self.body.append('\n\\includegraphics{%s}' % fname)
            self.body.append('\n\\end{center}')
            self.body.append('\n\\end{figure}\n')
        else:
            self.body.append('%s\\includegraphics{%s}%s' %
                             (para_separator, fname, para_separator))
    raise nodes.SkipNode


def latex_visit_smachinenode(self, node):
    render_smachine_latex(self, node, node['fsm'])


def render_smachine_texinfo(self, node, smachine):
    fname, outfn = render_smachine(self, smachine, 'png')
    if fname is not None:
        self.body.append('\n\n@float\n')
        caption = node.get('caption')
        if caption:
            self.body.append('@caption{%s}\n' % self.escape_arg(caption))
        self.body.append('@image{%s,,,[smachinenode],png}\n'
                         '@end float\n\n' % fname[:-4])
    raise nodes.SkipNode


def texinfo_visit_smachinenode(self, node):
    render_smachine_texinfo(self, node, node['fsm'])


def text_visit_smachinenode(self, node):
    self.add_text('[graph]')


def man_visit_smachinenode(self, node):
    self.body.append('[graph]')
    raise nodes.SkipNode


def setup(app):
    """Sphinx setup."""
    app.add_node(smachinenode,
                 html=(html_visit_smachinenode, None),
                 latex=(latex_visit_smachinenode, None),
                 texinfo=(texinfo_visit_smachinenode, None),
                 text=(text_visit_smachinenode, None),
                 man=(man_visit_smachinenode, None))
    app.add_directive('ginsfsm', GinsFSMDirective)
