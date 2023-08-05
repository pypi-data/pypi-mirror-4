#!/usr/bin/env python
"""
Module MAIL -- Email Utilities
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from email.Message import Message
from email.Utils import formatdate
import smtplib


def sendmail(fromaddr, toaddr, subject, payload, headers=None,
             mimetype="text/plain", charset="us-ascii", msgdate=None,
             server='localhost', portnum=25, username=None, password=None):
    """Send an email.
    
    This is a simple utility function to allow programs
    to send simple emails without having to grovel into
    the depths of the python stdlib email package. It takes
    the following parameters, which should generally be in
    a format that complies with the email RFCs:
    
    - ``fromaddr`` - the "From" address
    
    - ``toaddr`` - the "To" address
    
    - ``subject`` - what goes in the "Subject" line
    
    - ``payload`` - the actual message.
    
    The above four parameters must always be supplied, as
    positional arguments. The rest of the parameters are
    optional, and can be supplied as keyword arguments (the
    preferred method):
    
    - ``headers`` - if present, a dictionary of header names and
      values; you should only use "X-" header names here (the
      Python email library fills in all the RFC standard headers
      for you, so you only need to worry about ones that are
      specific to your use case)
    
    - ``mimetype`` - the MIME type of the message; defaults to
      text/plain, and I would really like it if you *never*
      overrode that, since I'm highly allergic to HTML email :-)
    
    - ``charset`` - the character set of the message; defaults
      to us-ascii, since that's the easiest type to use for
      text/plain, but any charset that's compatible with the
      MIME type you're using will work
    
    - ``msgdate`` - the send date/time of the message; defaults
      to the current system date/time (you should only override
      this if you know your system clock is inaccurate or not
      configured properly)
    
    - ``server`` - the SMTP server to connect to; the default
      of localhost probably won't work unless you have a full
      MTA running on your machine (which you may under Linux,
      but most probably won't on a Mac, and won't unless hell
      freezes over on Windows...)
    
    - ``portnum`` - the port to connect to on the server; the
      default is the standard SMTP port, but servers that will
      do SSL/TLS (see below) often change the port
    
    - ``username`` - the username to authenticate to the server;
      if this is present, SSL/TLS will be used, and if a password
      is required, the ``password`` argument must be present
    
    - ``password`` - the password to authenticate to the server
    """
    
    msg = Message()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Date'] = msgdate or formatdate()
    msg['Subject'] = subject
    if headers:
        for hname, hvalue in headers.iteritems():
            msg['X-%s' % hname] = hvalue
    msg.set_type(mimetype)
    msg.set_payload(payload, charset)
    server = smtplib.SMTP(server, int(portnum))
    server.set_debuglevel(1)
    if username and password:
        server.starttls()
        server.login(username, password)
    server.sendmail(fromaddr, [toaddr], msg.as_string())
    server.quit()
