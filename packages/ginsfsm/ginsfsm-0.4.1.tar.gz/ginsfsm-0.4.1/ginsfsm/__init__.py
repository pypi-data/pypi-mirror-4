# -*- encoding: utf-8 -*-
"""
A python library to do development based in Finite State Machines.
"""
__version__ = '0.4.1'
__title__ = 'ginsfsm'
__author__ = 'Ginés Martínez'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2013 Ginés Martínez'


# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
