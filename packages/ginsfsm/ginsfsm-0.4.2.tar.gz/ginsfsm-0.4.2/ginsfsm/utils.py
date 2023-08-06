# -*- coding: utf-8 -*-
from .compat import text_type


def string_to_bytearray(s):
    if isinstance(s, text_type):
        s = bytearray(s, encoding="utf-8", errors="strict")
    else:
        s = bytes(s)
    return s


def string_to_pack(s):
    if isinstance(s, text_type):
        s = bytearray(s, encoding="utf-8", errors="strict")
    s = bytes(s)
    return s


HEX_FILTER = ''.join(
    [(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)]
    )


def hexdump(prefix, src, length=16):
    N = 0
    result = ''
    src = bytes(src)
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02X" % ord(x) for x in s])
        s = s.translate(HEX_FILTER)
        result += "%s %04X: %-*s  %s\n" % (prefix, N, length*3, hexa, s)
        N += length
    return result
