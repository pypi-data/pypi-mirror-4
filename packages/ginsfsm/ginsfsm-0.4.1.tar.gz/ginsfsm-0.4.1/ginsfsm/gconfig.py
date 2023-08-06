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
)

import logging  # use root logger

accepted_types = (str, int, bool, list, tuple, dict)


class GConfigTemplateError(Exception):
    """ Raised when something is wrong in the :term:`gconfig-template`
    definition."""


class GConfigValidateError(Exception):
    """ Raised when something is a parameter is not validated."""


def add_gconfig(gconfig, new_gconfig):
    """ Add to gconfing a new_gconfig """
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


class GConfig(object):
    """Global configuration system.

    :param template: a dictionary or a list of dictionary
        describing the template of configuration parameters,
        with key/value as::

        'parameter_name': [type, default_value, flag, validate_function, description]

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
    def __init__(self, templates):
        self._gconfig_template = {}
        if not isinstance(templates, (list, tuple)):
            templates = [templates]

        for template in templates:
            if not issubclass(template.__class__, dict):
                raise GConfigTemplateError("GConfig(\"%s\") template in %s is not"
                            " a dict" % (repr(template), self.__class__.__name__))
            for parameter_name, definition in iteritems_(template):
                if not isinstance(parameter_name, string_types) or \
                        len(parameter_name) == 0:
                    raise GConfigTemplateError("Parameter name %s in %s is not"
                            " a string" %
                                (repr(parameter_name),
                                 self.__class__.__name__))
                if not isinstance(definition, (list, tuple)):
                    raise GConfigTemplateError("Parameter definition %s in %s is"
                            "  not a list or tuple" %
                                (repr(definition),
                                 self.__class__.__name__))
                if len(definition) != 5:
                    raise GConfigTemplateError("Parameter definition %s in %s is"
                            "  not a list or tuple of 5 items" %
                                (repr(definition),
                                 self.__class__.__name__))
                type_, default, flag, validate, desc = definition
                if validate is not None and not callable(validate):
                    raise GConfigTemplateError("Parameter definition %s in %s:"
                            "  %s is not a callable" %
                                (repr(definition), self.__class__.__name__,
                                repr(validate)))
                if desc is not None and not isinstance(desc, string_types):
                    raise GConfigTemplateError("Parameter definition %s in %s:"
                            "  %s is not a string" %
                                (repr(definition), self.__class__.__name__,
                                repr(desc)))
                if type_ is not None and not issubclass(type_, accepted_types):
                    raise GConfigTemplateError("Parameter definition %s in %s:"
                            "  %s is not a type in %s" %
                                (repr(definition), self.__class__.__name__,
                                repr(type_), accepted_types))

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
            except:
                # In real time don't raise exceptions, only at setup
                pass

    def filter_parameters(self, **settings):
        """ Filter the parameters in settings belongs to gobj.
        The gobj is searched by his named-gobj or his gclass name.
        The parameter name in settings, must be a dot-named,
        with the first item being the named-gobj o gclass name.
        """
        parameters = {}
        gobj_name = self.name

        for key, value in iteritems_(settings):
            names = key.rsplit('.', 1)
            if len(names) > 1:
                name = names[0]
                if gobj_name and gobj_name == name:
                    # search by named-gobj
                    parameters[names[1]] = value
                elif self.__class__.__name__ == name:
                    # search by gclass name
                    parameters[names[1]] = value
                elif name == 'GObj':
                    parameters[names[1]] = value
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
            logging.error("ERROR write_parameter (%s=%s): %s" % (
                str(parameter), str(value),
                "PARAMETER NAME INVALID"))
            return
        try:
            value = self._check(definition, value)
        except ValueError as e:
            logging.error("ERROR cannot write_parameter (%s=%s): %s" % (
                str(parameter), str(value), e))
            raise GConfigValidateError(
                "ERROR cannot check parameter (%s=%s)" % (
                str(parameter), str(value)))

        validate = definition[3]
        if validate is not None:
            ret = False
            try:
                ret = validate(value)
            except:
                pass
            finally:
                if not ret:
                    logging.error("ERROR cannot validate parameter (%s,%s)"
                        % (str(parameter), str(value)))
                    raise GConfigValidateError(
                        "ERROR cannot validate parameter (%s=%s)" % (
                        str(parameter), str(value)))

        if isinstance(value, string_types):
            prefix = value.split(':', 1)
            if prefix[0] == 'app':
                value = get_global_app(prefix[1])
                if not value:
                    logging.error("ERROR get_global_app (%s) NOT LOADED" %
                                  prefix[1])

        if hasattr(self, parameter):
            attr = getattr(self, parameter)
            if callable(attr):
                if not callable(value):
                    # Override methods only with callables
                    if value is not None:
                        logging.error("ERROR cannot override parameter (%s,%s)"
                            % (str(parameter), str(value)))
                    return
        setattr(self, parameter, value)

    def read_parameters(self):
        """ Return a dictionary with the current parameter:value pairs.
        """
        params = self.__dict__.copy()
        params.pop('_gconfig_template')
        return params

    def read_parameter(self, parameter):
        """ Return the current value of parameter.
        """
        try:
            value = getattr(self, parameter)
        except AttributeError:
            # In real time, we log the errors instead of raise.
            logging.error("ERROR doesn't exist parameter (%s)" % (str(parameter)))
            return None
        return value

    def _check(self, definition, value):
        # [type, default_value, flag, validate_function, desc]
        type_ = definition[0]
        if type_ is None:
            pass
        elif issubclass(type_, string_types):
            if value is not None:
                value = str(value)
        elif issubclass(type_, bool):  # first bool: it's a int type too!!
            value = asbool(value)
        elif issubclass(type_, integer_types):
            value = int(value)
        elif issubclass(type_, list):
            value = list(value)
        elif issubclass(type_, dict):
            value = dict(value)
        elif issubclass(type_, tuple):
            value = tuple(value)
        else:
            raise ValueError('Unknown type %s' % repr(value))
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
