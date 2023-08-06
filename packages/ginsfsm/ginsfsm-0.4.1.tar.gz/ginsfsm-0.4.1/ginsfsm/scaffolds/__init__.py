import binascii
import os

from ginsfsm.compat import native_

from ginsfsm.scaffolds.template import Template  # API


class GinsFSMTemplate(Template):
    """
     A class that can be used as a base class for GinsFSM scaffolding
     templates.
    """
    def pre(self, command, output_dir, vars):
        """ Overrides :meth:`ginsfsm.scaffold.template.Template.pre`, adding
        several variables to the default variables list (including
        ``random_string``, and ``package_logger``).  It also prevents common
        misnamings (such as naming a package "site" or naming a package
        logger "root".
        """
        if vars['package'] == 'site':
            raise ValueError('Sorry, you may not name your package "site". '
                             'The package name "site" has a special meaning in '
                             'Python.  Please name it anything except "site".')
        vars['random_string'] = native_(binascii.hexlify(os.urandom(20)))
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):  # pragma: no cover
        """ Overrides :meth:`ginsfsm.scaffold.template.Template.post`, to
        print "Welcome to GinsGSM.  Sorry for the convenience." after a
        successful scaffolding rendering."""
        self.out('Welcome to GinsFSM.  Sorry for the convenience.')
        return Template.post(self, command, output_dir, vars)

    def out(self, msg):  # pragma: no cover (replaceable testing hook)
        print(msg)


class SimpleGObjTemplate(GinsFSMTemplate):
    _template_dir = 'simple_gobj'
    summary = 'Create a simple GObj proyect.'


class SimpleWsgiTemplate(GinsFSMTemplate):
    _template_dir = 'simple_wsgi'
    summary = 'Create a simple WSGI proyect with pyramid.'


class MultipleWsgiTemplate(GinsFSMTemplate):
    _template_dir = 'multiple_wsgi'
    summary = 'Create a multiple WSGI proyect with pyramid.'

