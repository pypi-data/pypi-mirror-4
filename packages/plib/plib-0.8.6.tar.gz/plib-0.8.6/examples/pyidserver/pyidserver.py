#!/usr/bin/env python
"""
PYIDSERVER.PY
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of IDServer, a command-line tool
to query an internet server and return information
about it.
"""

import sys
import os
import socket

from plib.io.classes import chat_replies


def do_output(fileobj, s, linesep=True):
    fileobj.write(s)
    if linesep:
        fileobj.write(os.linesep)
    fileobj.flush()


def output_chat_replies(chat_addr, chat_items, fileobj,
    start_msg, conn_msg, close_msg):
    
    class _chat(chat_replies):
        def __init__(self, addr, items):
            do_output(fileobj, start_msg)
            super(_chat, self).__init__(addr, items)
        def on_connect(self):
            do_output(fileobj, conn_msg)
        def on_close(self):
            do_output(fileobj, close_msg)
    
    for reply in _chat(chat_addr, chat_items):
        do_output(fileobj, reply, False)


PROTO_DEFAULT = 'http'

quitmsgs = [None, "QUIT\r\n"]

protocols = {
    'ftp': (21, [None]),
    'http': (80, ["HEAD / HTTP/1.0\r\n\r\n"]),
    'imap': (143, [None, "A1 CAPABILITY\r\n", "A2 LOGOUT\r\n"]),
    'news': (119, quitmsgs),
    'pop': (110, quitmsgs),
    'smtp': (25, quitmsgs) }


def run_idserver(arg, dns_only, protocol, portnum, fileobj):
    
    if '://' in arg:
        addrtype, arg = arg.split('://')
        if addrtype in protocols:
            if protocol:
                do_output(fileobj,
                    "URL includes protocol %s, ignoring specified protocol %s."
                    % (addrtype, protocol))
            protocol = addrtype
        elif addrtype:
            do_output(fileobj,
                "URL includes incorrect protocol %s, ignoring."
                % addrtype)
    if '/' in arg:
        arg, path = arg.split('/')
        if path:
            do_output(fileobj, "URL includes path, ignoring.")
    if ':' in arg:
        arg, portstr = arg.split(':')
        try:
            p = int(portstr)
            if p != portnum:
                if portnum != 0:
                    do_output(fileobj,
                        "URL includes port %d, ignoring specified port %d."
                        % (p, portnum))
                portnum = p
        except ValueError:
            do_output(fileobj,
                "URL includes invalid port %s, ignoring." %
                portstr)
    
    if dns_only:
        do_output(fileobj, "Doing DNS lookup on %s ..." % arg)
    else:
        proto_msg = port_msg = ""
        if protocol == "":
            protocol = PROTO_DEFAULT
        else:
            protocol = protocol.lower()
            proto_msg = " using %s" % protocol
        if protocol in protocols:
            proto_port, proto_items = protocols[protocol]
            if portnum == 0:
                portnum = proto_port
            else:
                port_msg = " on port %i" % portnum
        else:
            raise ValueError, "Invalid protocol: %s." % protocol
    
    ipaddr = socket.gethostbyname(arg)
    if ipaddr == arg:
        # URL was an IP address, reverse lookup
        url = socket.gethostbyaddr(ipaddr)[0]
        do_output(fileobj, "Domain name for %s is %s." % (ipaddr, url))
    else:
        # URL was a domain name, normal lookup
        url = arg
        do_output(fileobj, "IP address for %s is %s." % (url, ipaddr))
    
    if not dns_only:
        output_chat_replies((url, portnum), proto_items, fileobj,
            "Contacting %s%s%s ..." % (arg, proto_msg, port_msg),
            "Connected ...%sServer returned the following:%s" %
                (os.linesep, os.linesep),
            "Connection closed.")


def run_main(arg, outfile=None, errfile=None,
        dns_only=False, protocol="", portnum=0):
    """Query server and write results to a file-like object.
    
    This is the intended external API for pyidserver; it wraps the
    ``run_idserver`` function, which does the work, with reasonable
    error handling and diagnostic output.
    
    The purpose of pyidserver is to query an internet server for
    basic information, and output it to the user. It does not actually
    "speak" any of the specific protocols for which it will query a
    server; it relies on the fact that most servers return some sort
    of informational "greeting" when a client connects to them, and
    the information it outputs is taken from such greetings.
    
    In the case of HTTP servers, a request must first be sent for the
    server to return any information (a HEAD request is used for this
    purpose). In the case of IMAP servers, an additional request after
    the first greeting (A1 CAPABILITY) is used to elicit additional
    information.
    
    In all cases where the session with the server is supposed to be
    explicitly terminated (all protocols supported except FTP),
    pyidserver does the termination when it is finished.
    
    Arguments:
    
    - ``arg``: a URL string (either an IP address or a host name).
      May include a protocol specifier at the start (e.g., http://),
      and may include a port specifier at the end (e.g., :80). A
      trailing slash, '/', in the URL, and anything after it, are
      treated as a path specifier and ignored.
    
    - ``outfile``: the file-like object for output (actually it
      can be anything that has ``write`` and ``flush`` methods).
      Defaults to standard output.
    
    - ``errfile``: a file-like object for error output (actually it
      can be anything with a ``write`` method). Defaults to the same
      object as ``outfile``.
    
    - ``dns_only``: If true, only a DNS lookup is done; no connection
      is actually made to the server.
    
    - ``protocol: one of the strings listed as keys in the
      ``protocols`` dictionary above (the default, if nothing is
      passed, is 'http').
    
    - ``portnum``: an integer giving the port number on the server.
      (This parameter should only need to be used very rarely;
      almost always the port number is determined by the protocol
      as shown in the dictionary above.)
    """
    
    if outfile is None:
        outfile = sys.stdout
    if errfile is None:
        errfile = outfile
    try:
        run_idserver(arg, dns_only, protocol, portnum, outfile)
    except ValueError:
        errfile.write("%s%s" % (str(sys.exc_info()[1]), os.linesep))
    except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        exc_type, exc_value, _ = sys.exc_info()
        errfile.write("%s %s%s" % (str(exc_type), str(exc_value), os.linesep))


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    _, __, def_dns, def_proto, def_port = run_main.func_defaults
    optlist = (
        ("-l", "--lookup", { 'action': "store_true",
            'dest': "dns_only", 'default': def_dns,
            'help': "Only do DNS lookup, no server query" } ),
        ("-p", "--protocol", { 'action': "store", 'type': str,
            'dest': "protocol", 'default': def_proto,
            'help': "Use the specified protocol to contact the server" } ),
        ("-r", "--port", { 'action': "store", 'type': int,
            'dest': "portnum", 'default': def_port,
            'help': "Use the specified port number to contact the server" } )
        )
    arglist = ["url"]
    
    opts, args = parse_options(optlist, arglist)
    # Spot check the parsing results
    assert opts['dns_only'] == opts.dns_only
    assert args[0] == args.url
    
    run_main(args.url, sys.stdout, sys.stderr,
        opts.dns_only, opts.protocol, opts.portnum)
