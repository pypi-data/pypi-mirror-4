# -*- coding: utf-8 -*-

import socket


def netcat(hostname, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    while 1:
        data = s.recv(1024)
        if data == "":
            break
        print data.strip()
    s.close()


def monitor(zope2Cmd, *args):
    """
    Ask for monitoring probe to five.z2monitor using tcp
    """
    productConfig = zope2Cmd.options.configroot.product_config
    z2monitorConfig = productConfig.get('five.z2monitor')
    if z2monitorConfig is None:
        raise KeyError('Cannot find five.z2monitor section in Zope instance configuration')
    hostname, port = z2monitorConfig.get('bind').split(':')
    if args == ('',):
        content = 'help'
    else:
        content = ' '.join(args)
    netcat(hostname, int(port), '%s\n' % content)
