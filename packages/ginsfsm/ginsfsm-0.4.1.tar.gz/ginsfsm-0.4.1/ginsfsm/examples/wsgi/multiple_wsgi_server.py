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
#from ginsfsm.protocols.wsgi.common.urlmap import URLMap


#===============================================================
#                   Wsgi apps
#===============================================================
def application1(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World ONE!\n'


def application2(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World TWO!\n'


def application3(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World THREE!\n'


def paste_app_factory1(global_config, **local_conf):
    return application1


def paste_app_factory2(global_config, **local_conf):
    return application2


def paste_app_factory3(global_config, **local_conf):
    return application3


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
        application=application
    )
    return ga


if __name__ == "__main__":
    """ You can run directly this file, without gserve.
    """
    from ginsfsm.protocols.wsgi.common.urlmap import (
        URLMap,
        parse_path_expression,
    )
    local_conf = {
        '/': application1,
        '/app2': application2,
        '/app3': application3,
    }

    urlmap = URLMap()
    for path, app in local_conf.items():
        path = parse_path_expression(path)
        urlmap[path] = app

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
        urlmap,
    )

    ga = main({}, **local_conf)

    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
