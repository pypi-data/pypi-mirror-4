# -*- encoding: utf-8 -*-
"""
Pyramid root entry point

.. autoclass:: PyramidRoot
    :members:

:func:`pyramid_application`.

"""

from pyramid.config import Configurator
from pyramid.security import (
    Allow,
    Everyone,
    ALL_PERMISSIONS,
)

from ginsfsm.globals import get_global_app
from ginsfsm.gobj import GObj
from .pyramid_main import TestSocksjsApps


#----------------------------------------------------------------------#
#                           Pyramid root
#----------------------------------------------------------------------#
PYRAMIDROOT_GCONFIG = {
}


class PyramidRoot(GObj):
    """ Pyramid root.
        Must be a gobj with an empty name.
    """
    __acl__ = [
        (Allow, Everyone, ALL_PERMISSIONS)
    ]

    def __init__(self):
        GObj.__init__(self, {}, PYRAMIDROOT_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        self.pyramid_app = self.create_gobj(
            '__test_sockjs__',
            TestSocksjsApps,
            self,
        )

pyramid_root = None


def make_root(gaplic):
    global pyramid_root
    if pyramid_root is None:
        pyramid_root = gaplic.create_gobj(
            None,   # pyramid resources tree root MUST be unnamed.
            PyramidRoot,
            None,
        )
    return pyramid_root


def get_root(request):
    return pyramid_root


#-------------------------------------------------#
#       Paste entry point
#       Pyramid wsgi-app configuration
#-------------------------------------------------#
def pyramid_application(global_config, **local_conf):
    """ Paste entry point.

        Returns a WSGI application.
    """
    if 'gaplic' in local_conf:
        gaplic_name = local_conf.pop('gaplic')
    else:
        raise Exception('You must supply a gaplic name in ini file.')

    gaplic = get_global_app(gaplic_name)
    if not gaplic:
        raise Exception("gaplic '%s' supplied for wsgi is invalid" %
                        gaplic_name)

    config = Configurator(
        root_factory=get_root,
        settings=local_conf,
    )

    # Set up views
    config.include("ginsfsm.protocols.sockjs.server")

    make_root(gaplic)

    return config.make_wsgi_app()
