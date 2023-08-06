# -*- coding:utf-8; tab-width:4; mode:python -*-

from types import NoneType
import socket

from .os_ import SubProcess
from .type_ import checked_type


def is_port_open(port, proto='tcp', host=None):
    def localport():
        sp = SubProcess('fuser -n {0} {1}'.format(proto, port))
        return sp.wait() == 0

    def remoteport():
        s = socket.socket()
        s.settimeout(1)
        try:
            s.connect((host, port))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return True
        except socket.error:
            return False

    port = checked_type(int, port)
    host = checked_type((str, NoneType), host)

    if host in [None, 'localhost', '127.0.0.1']:
        return localport()

    assert proto == 'tcp', "proto %s not supported yet" % proto

    return remoteport()


def is_host_reachable(host):
    sp = SubProcess('ping -c 1 {0}'.format(host))
    return sp.wait() == 0
