# -*- coding: utf-8 -*-

import smtpd
import asyncore
import optparse

DESCRIPTION = "Invenio mail server for development"
USAGE_MESSAGE = "mailserve [-bp]"

def printing_smtpd(addr, port):
    """
    Start a mail debug server

    Remember to update your invenio-local.cfg
    """
    addr = addr
    try:
        port = int(port)
    except Exception:
        print("%s is not a valid port number." % port)
        return

    try:
        print """Remember to set the two following settings in invenio-local.conf:

CFG_MISCUTIL_SMTP_HOST=%s
CFG_MISCUTIL_SMTP_PORT=%s
"""  % (addr, port)

        print "Now accepting mail at %s:%s (hit CONTROL-C to stop)" % (addr, port)
        smtpd.DebuggingServer((addr, port), None)
        asyncore.loop()
    except KeyboardInterrupt:
        print 'Exiting'


def parse_cli_options():
    """Parse command line options"""
    parser = optparse.OptionParser(description=DESCRIPTION,
                                   usage=USAGE_MESSAGE)
    # Display help and exit
    parser.add_option('-b', dest='bind_address', default='127.0.0.1',
                                                    help='Address to bind to')
    parser.add_option('-p', dest='bind_port', type='int', default=1025,
                                    help='Port to bind to')
    return parser.parse_args()


def _main():
    """Script entrance"""
    (options, args) = parse_cli_options()

    printing_smtpd(options.bind_address, options.bind_port)


def main():
    try:
        _main()
    except KeyboardInterrupt:
        print 'Exiting'


if __name__ == '__main__':
    main()
