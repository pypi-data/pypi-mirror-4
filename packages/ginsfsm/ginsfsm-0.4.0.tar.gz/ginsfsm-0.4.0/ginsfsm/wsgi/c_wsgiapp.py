# -*- encoding: utf-8 -*-

import time
import traceback
import logging

from .parser import HTTPRequestParser
from .task import (
    ErrorTask,
    WSGITask,
    )
from .utilities import (
    InternalServerError,
    )

from ginsfsm.gobj import GObj
from ginsfsm.deferred import DeferredInterrupt


def ac_execute_requests(self, event):
    """Execute all pending requests """
    requests = event.requests
    gsock = self.gsock
    ext_event = None
    if hasattr(event, 'ext_event'):
        ext_event = event.ext_event
    while requests:
        request = requests[0]
        if request.error:
            task = ErrorTask(self.wsgi_server, gsock, request)
        else:
            # Añado esto en get_environment de task.py,despues de environ = {}
            # environ['gobj.gsock'] = gsock
            task = WSGITask(self.wsgi_server, gsock, request, ext_event)
        try:
            task.service()
        except DeferredInterrupt as e:

            def callback(request, ext_event=None):
                self.send_event(
                    self,
                    'EV_EXECUTE_REQUESTS',
                    requests=[request],
                    ext_event=ext_event,
                )
            self.gaplic.deferred_list.add_callback(
                e.deferred_ref,
                callback,
                request
            )
        except:
            logging.exception('Exception when serving %s' %
                                  task.request.path)
            if not task.wrote_header:
                if self.expose_tracebacks:
                    body = traceback.format_exc()
                else:
                    body = ('The server encountered an unexpected '
                            'internal server error')
                request = HTTPRequestParser(
                    url_scheme=self.wsgi_server.url_scheme)
                request.error = InternalServerError(body)
                task = ErrorTask(self.wsgi_server, gsock, request)
                task.service()  # must not fail
            else:
                task.close_on_finish = True
        # we cannot allow self.requests to drop to empty til
        # here; otherwise the mainloop gets confused
        if task.close_on_finish:
            gsock.close_when_flushed = True
            for request in requests:
                request._close()
            requests = []
        else:
            request = requests.pop(0)
            request._close()

    gsock.send_some()
    gsock.last_activity = time.time()


WSGIAPP_FSM = {
    'event_list': (
        'EV_EXECUTE_REQUESTS: top input',
        'EV_WSGIAPP_RESPONSE: top output',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_EXECUTE_REQUESTS', ac_execute_requests,    'ST_IDLE'),
        ),
    }
}

WSGIAPP_GCONFIG = {
    'wsgi_server': [None, None, 0, None, "wsgi server"],
    'gsock': [None, None, 0, None, "clisrv gsock"],
    'expose_tracebacks': [bool, False, 0, None,
        "expose tracebacks of uncaught exceptions"],
}


class WSGIApp(GObj):
    """  Execute WSGI apps.
    """

    def __init__(self):
        GObj.__init__(self, WSGIAPP_FSM, WSGIAPP_GCONFIG)

    def start_up(self):
        pass
