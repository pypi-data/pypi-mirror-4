# -*- encoding: utf-8 -*-
""" basehandler
"""

import random
import hashlib
from pyramid.view import view_config

from ginsfsm.protocols.sockjs.server.proto import json
from ginsfsm.protocols.sockjs.server.basehandler import (
    PreflightHandler,
    BaseHandler,
)
from ginsfsm.gobj import GObj
from ginsfsm.gconfig import GConfig
from ginsfsm.protocols.sockjs.server.util import (
    str_to_bytes,
    MAXSIZE,
)

#----------------------------------------------------------------#
#                   Info GClass
#----------------------------------------------------------------#
GINFO_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GInfo(GObj):
    """  GInfo GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GINFO_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        # Info Test views
        """
        self.sockjs_server.pyramid_config.add_view(
            context=GInfo,
            name='',
            view=InfoHandler,
            attr='get',
            path_info=self.resource_path(),
            request_method='GET',
            permission=self.sockjs_server.permission,
        )
        self.sockjs_server.pyramid_config.add_view(
            context=GInfo,
            name='',
            view=InfoHandler,
            attr='options',
            path_info=self.resource_path(),
            request_method='OPTIONS',
            permission=self.sockjs_server.permission,
        )
        """


#----------------------------------------------------------------#
#                   Info views
#----------------------------------------------------------------#
@view_config(
    context=GInfo,
    name='',
    attr='get',
    request_method='GET',
)
@view_config(
    context=GInfo,
    name='',
    attr='options',
    request_method='OPTIONS',
)
class InfoHandler(PreflightHandler):
    """SockJS 0.2+ /info handler"""
    def __init__(self, context, request):
        PreflightHandler.__init__(self, context, request)
        self.access_methods = 'OPTIONS, GET'

    def get(self):
        response = self.response
        response.content_type = 'application/json'
        response.charset = 'UTF-8'
        self.preflight()
        self.disable_cache()

        disabled_transports = \
            self.context.sockjs_server.config.disabled_transports

        info = {
            'websocket': 'websocket' not in disabled_transports,
            'cookie_needed': self.context.sockjs_server.cookie_needed,
            'origins': ['*:*'],
            'entropy': random.randint(0, MAXSIZE),
        }
        response.body = json.dumps(info).encode()
        return response


#----------------------------------------------------------------#
#                   IFrame GClass
#----------------------------------------------------------------#
GIFRAME_GCONFIG = {
    'sockjs_server': [None, None, GConfig.FLAG_DIRECT_ATTR, None, ""],
}


class GIFrame(GObj):
    """  GIFrame GObj.
    """
    def __init__(self):
        GObj.__init__(self, {}, GIFRAME_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        """
        self.sockjs_server.pyramid_config.add_view(
            context=GIFrame,
#            name='',
            view=IFrameHandler,
            attr='get',
            path_info=self.resource_path(),
            request_method='GET',
            permission=self.sockjs_server.permission,
        )
        """

#----------------------------------------------------------------#
#                   IFrame views
#----------------------------------------------------------------#
IFRAME_TEXT = """<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <script>
    document.domain = document.domain;
    _sockjs_onload = function(){SockJS.bootstrap_iframe();};
  </script>
  <script src="%s"></script>
</head>
<body>
  <h2>Don't panic!</h2>
  <p>This is a SockJS hidden iframe. It's used for cross domain magic.</p>
</body>
</html>
""".strip()


@view_config(
    context=GIFrame,
    name='',
    attr='get',
    request_method='GET',
)
class IFrameHandler(BaseHandler):
    """SockJS IFrame page handler"""
    def get(self):
        response = self.response
        data = str_to_bytes(
            IFRAME_TEXT % self.context.sockjs_server.config.sockjs_url)
        hsh = hashlib.md5(data).hexdigest()

        #value = self.request.headers.get('If-None-Match')
        value = self.request.environ.get('HTTP_IF_NONE_MATCH')
        if value:
            if value.find(hsh) != -1:
                del response.headers['Content-Type']
                self.set_status(304)
                return response

        response.content_type = 'text/html'
        response.charset = 'UTF-8'
        self.enable_cache()
        self.set_header('Etag', hsh)
        response.body = data
        return response
