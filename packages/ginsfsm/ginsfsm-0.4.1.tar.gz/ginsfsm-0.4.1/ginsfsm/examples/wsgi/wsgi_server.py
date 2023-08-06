"""
Sample WSGI server
==================

It uses :class:`ginsfsm.wsgi.c_wsgi_server.GWSGIServer`.

.. autofunction:: main

"""

from ginsfsm.gaplic import GAplic
from ginsfsm.wsgi.c_wsgi_server import GWSGIServer


#===============================================================
#                   Server
#===============================================================
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield 'Hello World\n'


def paste_app_factory(global_config, **local_conf):
    return application


#===============================================================
#                   Main
#===============================================================
def main(global_config, **settings):
    """ Entry point to run with gserve (PasteDeploy)
    """
    ga = GAplic('Example6', **settings)
    ga.create_gobj(
        'wsgi-server',
        GWSGIServer,
        None,
        host='0.0.0.0',
        port=8000,
        application=application
    )
    return ga


if __name__ == "__main__":
    ga = main({})

    try:
        ga.mt_process()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
