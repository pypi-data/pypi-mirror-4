# -*- encoding: utf-8 -*-
"""
    WebsocketResponse -  an asynchronous Websocket WebOb Response over ginsfsm.
"""
from ginsfsm.protocols.http.server.c_http_clisrv import ResponseInterrupt

try:
    from pyramid.response import Response
except ImportError:  # pragma: no cover
    try:
        from webob import Response
    except ImportError:  # pragma: no cover
        raise Exception('async_response is depending of Pyramid or WebOb')


class WebsocketResponse(Response):
    def __init__(self, context, request):
        super(WebsocketResponse, self).__init__()
        self.context = context
        self.request = request

    def __call__(self, environ, start_response):
        "Override WSGI call"
        raise ResponseInterrupt()

