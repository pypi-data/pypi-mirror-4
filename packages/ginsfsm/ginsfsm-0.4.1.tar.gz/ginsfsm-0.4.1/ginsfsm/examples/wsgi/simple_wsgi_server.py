"""
Simple WSGI server
==================

It uses :class:`ginsfsm.protocols.wsgi.server.c_wsgi_server.GWsgiServer`.

.. autofunction:: main

"""

import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gaplic import GAplic
from ginsfsm.globals import get_global_app, set_global_app
from ginsfsm.protocols.wsgi.server.c_wsgi_server import GWsgiServer


#===============================================================
#                   Wsgi app
#===============================================================
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World\n'


def paste_app_factory(global_config, **local_conf):
    return application


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
    application = get_global_app(application)
    ga = GAplic('Wsgi-Example', **local_conf)
    ga.create_gobj(
        'wsgi-server',
        GWsgiServer,
        None,
        application=application,
    )
    return ga


if __name__ == "__main__":
    local_conf = {
        'GObj.trace_mach': True,
        'GObj.logger': logging,
        'GSock.trace_dump': True,
        'wsgi-server.host': '0.0.0.0',
        'wsgi-server.port': 8002,
        'application': 'wsgi-application',
    }
    set_global_app(
        'wsgi-application',
        paste_app_factory({}, **local_conf)
    )
    ga = main({}, **local_conf)

    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
