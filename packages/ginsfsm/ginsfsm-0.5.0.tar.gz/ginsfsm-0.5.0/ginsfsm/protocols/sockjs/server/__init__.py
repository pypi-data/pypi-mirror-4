"""
`Sockjs <https://github.com/sockjs>`_ server for
`ginsfsm <http://ginsfsm.org>`_
and
`Pyramid <http://docs.pylonsproject.org/en/latest/index.html>`_.

"""


def includeme(config):
    """Include the ginsfsm sockjs configuration
    """
    config.scan("ginsfsm.protocols.sockjs.server")
