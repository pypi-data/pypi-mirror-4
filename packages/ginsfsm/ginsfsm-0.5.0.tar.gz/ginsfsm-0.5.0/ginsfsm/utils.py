# -*- coding: utf-8 -*-
from ginsfsm.compat import (
    urlparse,
    text_type,
    bytes_,
)
from time import time
from hashlib import md5
from random import random


def random_key():
    """Return random session key"""
    i = md5()
    i.update(bytes_('%s%s' % (random(), time())))
    return i.hexdigest()


def string_to_bytearray(s, encoding='utf-8', errors='strict'):
    if isinstance(s, text_type):
        s = bytearray(s, encoding, errors)
    elif not isinstance(s, bytearray):
        s = bytearray(s)
    return s


def hexdump(prefix, byts, length=16):
    ''' hd: hexdump
    dump in hex with pretty formating the hex value and ascii value (if any)
    for a block of bytes [assumed to be a tuple]

    byts: incoming bytes
    length: how many bytes to display on each line.
    '''
    byts = string_to_bytearray(byts)
    n = 0
    result = ''
    while byts:
        b_work = byts[:length]
        byts = byts[length:]
        hexa = ' '.join(["%02X" % x for x in b_work])
        asc = ''.join([((((x < 32) or (x > 0x7e)) and '.') or chr(x)) for x in b_work])
        result += "%s %04X %-*s %s\n" % (prefix, n, length*3, hexa, asc)
        n += length
    return result


def get_path_from_url(url):
    o = urlparse.urlparse(url)
    return o.path


def get_host_port_from_urls(urls):
    routes = []
    for url in urls:
        o = urlparse.urlparse(url)
        if not o.hostname or not o.scheme:
            print("Can't get HOST from URL %r" % url)
            continue
        if not o.port:
            if o.scheme in ('wss', 'https'):
                port = 443
            elif o.scheme in ('ws', 'http'):
                port = 80
            else:
                port = 80
        else:
            port = o.port
        if not port:
            print("Can't get PORT from URL %r" % url)
            continue

        routes.append((o.hostname, port),)
    return routes
