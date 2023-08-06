"""
This module implements a flexible global configuration system.


.. autoclass:: GConfig
    :members: reset_all_parameters, reset_parameter, write_parameters,
     write_few_parameters, read_parameters, read_parameter

.. autoexception:: GConfigTemplateError

.. autoexception:: GConfigValidateError

"""

from ginsfsm.globals import get_global_app
from ginsfsm.compat import (
    iteritems_,
    string_types,
    integer_types,
    binary_type,
    bytes_,
)

accepted_types = (str, int, bool, list, tuple, dict, bytes)


class GConfigTemplateError(Exception):
    """ Raised when something is wrong in the :term:`gconfig-template`
        definition.
    """


class GConfigValidateError(Exception):
    """ Raised when something is a parameter is not validated.
    """


def add_gconfig(gconfig, new_gconfig):
    """ Add to gconfig a new_gconfig """
    if new_gconfig is None:
        return gconfig

    if gconfig is not None:
        if isinstance(gconfig, (list, tuple)):
            gconfig = list(gconfig)
            gconfig.append(new_gconfig)
        else:
            gconfig = [gconfig, new_gconfig]
    else:
        gconfig = [new_gconfig]
    return gconfig


class _Config(object):
    """ Collect config properties.
    """


class GConfig(object):
    """Global configuration system.

    :param template: a dictionary or a list of dictionary
        describing the template of configuration parameters,
        with key/value as::

            'parameter_name':
            [type, default_value, flag, validate_function, description]

    Each parameter is defined with a template, that it's a list of 4 elements:

    * type: must be a type of:
      ``str``, ``int``, ``bool``, ``list``, ``dict`` or ``tuple``.
    * default_value: default value.
    * flag: modify behaviour.
    * validate_function: ``None`` or a ``callable``.
      The ``callable`` must return ``True`` if validates the value,
      otherwise ``False``. If the callable return ``False``
      a :exc:`GConfigValidateError` will be raised.
    * description: String describing the parameter.

    If the template is not valid, a :exc:`GConfigTemplateError` exception
    is raised.
    """

    FLAG_DIRECT_ATTR = 0x01  # write directly in gobj (not in config attr).

    def __init__(self, templates, logger=None):
        self._gconfig_template = {}
        self.config = _Config()
        self.logger = logger

        if not isinstance(templates, (list, tuple)):
            templates = [templates]

        for template in templates:
            if not issubclass(template.__class__, dict):
                raise GConfigTemplateError(
                    "GConfig(%r) template in %r is not a dict" %
                    (template, self.__class__.__name__))
            for parameter_name, definition in iteritems_(template):
                if not isinstance(parameter_name, string_types) or \
                        len(parameter_name) == 0:
                    raise GConfigTemplateError(
                        "Parameter name %r in %r is not a string" %
                        (parameter_name, self.__class__.__name__))
                if not isinstance(definition, (list, tuple)):
                    raise GConfigTemplateError(
                        "Parameter definition %r in %r is not list or tuple" %
                        (definition, self.__class__.__name__))
                if len(definition) != 5:
                    raise GConfigTemplateError(
                        "Parameter definition %r in %r is"
                        "  not a list or tuple of 5 items" %
                        (definition, self.__class__.__name__))
                type_, default, flag, validate, desc = definition
                if validate is not None and not callable(validate):
                    raise GConfigTemplateError(
                        "Parameter definition %r in %r:"
                        "  %r is not a callable" % (
                            definition, self.__class__.__name__, validate))
                if desc is not None and not isinstance(desc, string_types):
                    raise GConfigTemplateError(
                        "Parameter definition %r in %r:"
                        "  %r is not a string" %
                        (definition, self.__class__.__name__, desc))
                if type_ is not None and not issubclass(type_, accepted_types):
                    raise GConfigTemplateError(
                        "Parameter definition %r in %r:"
                        "  %r is not a type in %r" %
                        (definition, self.__class__.__name__,
                        type_, accepted_types))

                # [type, default_value, flag, validate_function, desc]

                self._gconfig_template.update({parameter_name: definition})

        # create default parameter values.
        for parameter, definition in iteritems_(self._gconfig_template):
            value = definition[1]
            self._write_parameter(parameter, value)

    def reset_all_parameters(self):
        """ Reset all parameters to default values.
        """
        kw = {}
        for parameter, definition in iteritems_(self._gconfig_template):
            kw.update({parameter: definition[1]})
        self.write_parameters(**kw)

    def reset_parameter(self, parameter):
        """ Reset one parameter to his default value.
        """
        definition = self._gconfig_template.get(parameter, None)
        if definition is not None:
            value = definition[1]
        kw = {parameter: value}
        self.write_parameters(**kw)

    def write_few_parameters(self, parameter_list, **kw):
        """ Write a few parameters.

        :param parameters: write only the parameters in ``parameter_list``.

        :param kw: keyword arguments with parameter_name:value pairs.

        .. warning:: Only the parameters defined in the template are writted,
            the remaining are ignored.
        """
        for parameter, value in iteritems_(kw):
            if parameter not in parameter_list:
                continue
            try:
                self._write_parameter(parameter, value)
            except:
                # In real time don't raise exceptions, only at setup
                pass

    def write_parameters(self, **kw):
        """ Write parameters.

        :param kw: keyword arguments with parameter_name:value pairs.

        .. warning:: Only the parameters defined in the template are writted,
            the remaining are ignored.
        """
        for parameter, value in iteritems_(kw):
            try:
                self._write_parameter(parameter, value)
            except Exception as e:
                # In real time don't raise exceptions, only at setup
                if self.logger:
                    self.logger.exception(e)

    def filter_parameters(self, **settings):
        """ Filter the parameters in settings belongs to gobj.
        The gobj is searched by his named-gobj or his gclass name.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = {}
        named_gobj = self.name
        class_name = self.__class__.__name__

        for key, value in iteritems_(settings):
            names = key.rsplit('.', 1)
            if len(names) > 1:
                # Can be:
                #       GClass.attribute
                #       named-gobj.attribute
                name = names[0]
                attribute = names[1]
                if named_gobj and named_gobj == name:
                    # search by named-gobj
                    parameters[attribute] = value
                elif class_name == name:
                    # search by gclass name
                    parameters[attribute] = value
                elif name == 'GObj':
                    parameters[attribute] = value
            else:
                parameters[key] = value
        return parameters

    def _write_parameter(self, parameter, value):
        """ Write parameter. Raise and log the errors.
        Use: in setup we raise errors, in real time we log the errors.
        """
        # [type, default_value, flag, validate_function, desc]
        definition = self._gconfig_template.get(parameter, None)
        if definition is None:
            self.logger and self.logger.error(
                "ERROR %r in write_parameter(%r):"
                "\n  name = %r\n  value = %r" % (
                "PARAMETER NAME INVALID",
                self, parameter, value)
            )
            return

        validate = definition[3]
        type_ = definition[0]
        flag = definition[2]

        try:
            value = self._check(type_, value, validate)
        except Exception as e:
            msg = "ERROR %s in write_parameter(%r):" \
                "\n  name = %r\n  value = %r" % (
                e, self, parameter, value)
            self.logger and self.logger.exception(msg)
            raise GConfigValidateError(msg)

        if isinstance(value, string_types):
            # TODO: doc this!
            # TODO: move this to validate function
            prefix = value.split(':', 1)
            if prefix[0] == 'app':
                value = get_global_app(prefix[1])
                if not value:
                    self.logger and self.logger.error(
                        "ERROR get_global_app (%s) NOT LOADED" %
                        prefix[1])

        if flag and GConfig.FLAG_DIRECT_ATTR:
            destobj = self
        else:
            destobj = self.config

        if hasattr(destobj, parameter):
            attr = getattr(destobj, parameter)
            if callable(attr):
                if not callable(value):
                    # Override methods only with callables
                    if value is not None:
                        self.logger and self.logger.error(
                            "ERROR cannot override parameter (%r,%r)" % (
                                parameter, value))
                    return
        # OLD setattr(self, parameter, value)
        setattr(destobj, parameter, value)

    def _check(self, type_, value, validate):
        """ Check the value and convert into his definition type.
            With validate you can make special types.
        """
        if validate is not None:
            value = validate(value)

        if type_ is None:
            pass
        elif issubclass(type_, string_types):
            if value is not None:
                value = str(value)
        elif issubclass(type_, binary_type):
            if value is not None:
                value = bytes_(value)
        elif issubclass(type_, bool):  # first bool: it's a int type too!!
            value = asbool(value)
        elif issubclass(type_, integer_types):
            value = int(value)
        elif issubclass(type_, list):
            if isinstance(value, string_types):
                # this can have colateral effect
                value = value.replace(',', ' ')
                value = value.split()
            elif not hasattr(value, '__iter__'):
                value = [value, ]
            value = list(value)
        elif issubclass(type_, dict):
            value = dict(value)
        elif issubclass(type_, tuple):
            if isinstance(value, string_types):
                # this can have colateral effect
                value = value.replace(',', ' ')
                value = value.split()
            elif not hasattr(value, '__iter__'):
                value = (value,)
            value = tuple(value)
        else:
            raise ValueError('Unknown type %r' % value)
        return value

    def read_parameters(self):
        """ Return a dictionary with the current parameter:value pairs.
        """
        # OLD params = self.__dict__.copy()
        params = self.config.__dict__.copy()
        # OLD params.pop('_gconfig_template')
        return params

    def read_parameter(self, parameter):
        """ Return the current value of parameter.
        """
        # [type, default_value, flag, validate_function, desc]
        definition = self._gconfig_template.get(parameter, None)
        if not definition:
            # In real time, we log the errors instead of raise.
            self.logger and self.logger.error(
                "ERROR in %r, doesn't exist parameter (%r)" % (
                self, parameter))
            return None
        flag = definition[2]
        if flag and GConfig.FLAG_DIRECT_ATTR:
            read_in = self
        else:
            read_in = self.config

        try:
            # OLD value = getattr(self, parameter)
            value = getattr(read_in, parameter)
        except AttributeError:
            # In real time, we log the errors instead of raise.
            self.logger and self.logger.error(
                "ERROR in %r, doesn't exist parameter (%r)" % (
                self, parameter))
            return None
        return value


truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1'))


def asbool(s):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``s`` is any of ``t``, ``true``, ``y``, ``on``, or ``1``, otherwise
    return the boolean value ``False``.  If ``s`` is the value ``None``,
    return ``False``.  If ``s`` is already one of the boolean values ``True``
    or ``False``, return it."""
    if s is None:
        return False
    if isinstance(s, bool):
        return s
    s = str(s).strip()
    return s.lower() in truthy
