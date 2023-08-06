# -*- encoding: utf-8 -*-
"""
Simple Sockjs server
====================

It uses :class:`ginsfsm.protocols.wsgi.server.c_wsgi_server.GWsgiServer`.

You can run this file with ``gserve test_sockjs_server.ini``

.. autofunction:: main

"""

import logging
logging.basicConfig(level=logging.WARN)

from ginsfsm.gaplic import GAplic
from ginsfsm.globals import (
    set_global_app,
    set_global_main_gaplic,
)

from ginsfsm.protocols.wsgi.server.c_wsgi_server import GWsgiServer


#===============================================================
#       Paste app factory.
#       To run with gserve yyy.ini
#===============================================================
def paste_app_factory(global_config, **local_conf):
    from ginsfsm.examples.sockjs.test_sockjs_apps import pyramid_application
    return pyramid_application(global_config, **local_conf)


#===============================================================
#                   Main
#===============================================================
def main(global_config, **local_conf):
    """ Entry point to run with gserve (PasteDeploy)
    """
    if 'application' in local_conf:
        application = local_conf.pop('application')
    else:
        raise Exception('You must supply an wsgi application.')
    ga = GAplic('ga', **local_conf)
    set_global_main_gaplic(ga)
    ga.create_gobj(
        'test-sockjs',
        GWsgiServer,
        ga,
        application=application,
    )
    return ga


if __name__ == "__main__":
    """ You can run directly this file, without gserve.
    """
    import logging
    logging.basicConfig(level=logging.WARN)
    # simulate running from ini file
    local_conf = {
        'GObj.trace_mach': False,
        'GObj.logger': logging,
        'GSock.trace_dump': False,
        'GWsgiServer.host': '0.0.0.0',
        'GWsgiServer.port': 8080,
        'application': 'wsgi-application',
    }

    ga = main({}, **local_conf)

    applic_settings = {
        'pyramid.reload_templates': True,
        'pyramid.debug_authorization': False,
        'pyramid.debug_notfound': False,
        'pyramid.debug_routematch': False,
        'pyramid.debug_templates': True,
        'pyramid.default_locale_name': 'en',
        'gaplic': 'ga'
    }

    set_global_app(
        'wsgi-application',
        paste_app_factory({}, **applic_settings)
    )

    try:
        ga.start()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
