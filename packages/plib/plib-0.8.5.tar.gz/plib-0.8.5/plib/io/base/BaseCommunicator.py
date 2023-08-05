#!/usr/bin/env python
"""
Module BaseCommunicator
Sub-Package IO of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the BaseCommunicator class, a base class that
implements common baseline communication functionality for all
I/O modes (serial vs. socket, blocking/synchronous vs.
non-blocking/asynchronous, etc.). This class assumes that a
subclass of ``BaseData`` is earlier in the MRO, so that all
of the methods implemented in that class can be accessed via
super calls.
"""


class BaseCommunicator(object):
    """Base class for managing a communication channel.
    
    Two key concepts are encoded in this class:
    
    - A "channel" is a communication link between an instance
      of this class and another endpoint.
    
    - A "communication loop" is a specific exchange of data
      over the channel (not necessarily a single round trip, but
      a single "exchange" conceptually--e.g., a "handshaking"
      protocol may require multiple round trips, but conceptually
      it is a single exchange).
    
    The two are not necessarily the same: the channel may stay
    alive over multiple communication loops with the same remote
    endpoint (this is what the ``keep_alive`` flag determines).
    The key thing with the communication loop is that while it is
    running, it controls program execution; whatever user code
    started it will not be returned control until it finishes.
    (User code may run in event handlers that are triggered, e.g.,
    when a server accepts a new connection, or when received data
    is ready to be processed; but those handlers must always
    return control to the communication loop.) In practice, as
    will be seen below, most of the time the lifetime of the
    channel and the communication loop is the same, but they
    should be kept conceptually distinct.
    
    Derived classes from this one will be one of three types; it
    should be noted that only with the second of the three (clients)
    is there an actual separation in practice between the lifetime
    of the communication loop and the channel.
    
    - Server-side communicators: These are request handlers or
      servers that only have one channel at a time (e.g., serial
      servers). If they do not shut down the connection after a
      single round-trip data exchange (as, for example, a simple
      HTTP server might do), their communication loop is entirely
      controlled by the client (i.e., it only exits when the client
      closes the connection). Either way, the lifetime of their
      communication loop is the same as that of the channel.
    
    - Client-side communicators: These open channels to servers,
      do some communicating, then exit. There are three subtypes
      of clients: (1) those that do a single round-trip data
      exchange and exit (the default as the base classes are set
      up); (2) those that may start with multiple data items queued,
      do as many round-trips as they have items queued, and then
      exit (e.g., a message delivery client that talks to a logging
      daemon--it may have one or more messages, but once it has
      delivered them all and received acknowledgement, it exits);
      (3) those that want to maintain a long-lived connection for
      an unspecified number of data exchanges (e.g., an instant
      messaging client driven by user interaction). It is the third
      type that will have a different lifetime for the communication
      loop and the channel (e.g., each instant message will be one
      communication loop; the loop then has to exit to allow the
      user to input a new message, then start up again, but the
      channel remains open the whole time).
    
    - Persistent communicators: These can be client-side or
      server-side (in which case they basically behave the same as
      clients or servers/request handlers with ``keep_alive`` set
      to ``True``), but the real intended use case for these is for
      enabling multiple long-running server processes to exchange
      messages at arbitrary times and in arbitrary order. Since
      new messages are injected into their communication loops by
      automated means rather than by user interaction, in practice
      the lifetime of the communication loop for these is the same
      as that of the channel.
    
    All communicator classes assume that there is a data handling
    class (intended to be ``BaseData`` or a class derived from it)
    earlier in the MRO, so that the presence of that API can be
    assumed. Communicators will override data handling methods as
    necessary to add the appropriate tracking of the state of the
    channel, making super calls to do the actual data handling.
    """
    
    keep_alive = False
    
    data_pending = False
    done = False
    finish_requested = False
    
    def start(self, data):
        """Push data to be sent over the channel.
         
        This method can be called from inside the communication loop
        (e.g., in the ``process_data`` method) as well as from outside.
        This method does the setup for further data transfer, which
        should prevent the communication loop from exiting (see the
        ``check_done`` method below).
        """
        
        self.data_pending = True
        self.done = False
        super(BaseCommunicator, self).start(data)
    
    def handle_write(self):
        """Clear the ``data_pending`` flag if all data has been written.
        
        Note that derived methods wrapping this one may call ``start``
        after this one returns, which will queue more data (e.g., see
        the ``PersistentMixin`` class).
        """
        
        super(BaseCommunicator, self).handle_write()
        if self.write_complete():
            self.data_pending = False
    
    def finish(self):
        """Close the channel once the current data transfer is complete.
        
        This method is called automatically if the ``keep_alive`` field is
        ``False`` (the default). If that field is ``True`` (e.g., in the
        async persistent classes), user code must explicitly call this method
        while inside the communication loop to close the channel. (If the
        communication loop is not running--e.g., from user interaction in a
        console or GUI--the ``close`` method can be called to close the
        channel, but inside the loop that method should not be used because
        it will close the channel immediately, even if there is still data
        to be processed; this method simply sets the flag that tells the loop
        to exit once the current transfer is complete.)
        """
        self.finish_requested = True
    
    def query_done(self):
        """Return ``True`` if no further read/write operations are necessary.
        
        This method is used to determine when the communication loop should
        be exited (see the ``check_done`` method). Whether that also closes
        the channel depends on the setting of the ``keep_alive`` flag.
        """
        return self.finish_requested or self.channel_closed()
    
    def check_done(self):
        """Check to see if the communication loop for this channel is done.
        
        This method is intended to be called whenever a single "pass"
        of the read/write cycle completes--i.e., ``self.write_data``
        and ``self.read_data`` have each been processed once. (Note
        that these semantics are altered somewhat for "persistent"
        asynchronous I/O--see the ``PersistentMixin`` class in the
        ``async`` sub-package.)
        
        Note that when this method is called, the ``clear_read`` and
        ``clear_write`` methods have already run, so any pending read
        and write data has been cleared. If this method, or any methods
        it calls (mainly ``query_done``), needs to make decisions based
        on sent or received data, that information must be stored before
        the data is cleared (typically in the ``process_data`` method)
        for it to be accessible here.
        
        If the ``keep_alive`` flag is not set, this method will call
        ``finish`` (meaning that the channel will close if ``query_done``
        returns true) unless something has been done to queue further
        data (e.g., calling the ``start`` method--see above).
        """
        
        if not (self.keep_alive or self.data_pending):
            self.finish()
        
        # Note that unless we override ``query_done``, the ``done`` flag
        # should only be ``True`` following this check (which will break
        # us out of the communication loop) if ``finish`` was called or
        # the channel was already closed by data handling (e.g., because
        # the other end of the channel shut down and the ``auto_close``
        # flag was set to ``True``)--i.e., on exit from this routine the
        # channel will always be closed if the communication loop is to
        # be exited, unless we override something. (The only classes in
        # this library that do that are the clients, which will exit
        # the loop if no data is pending, even if the channel remains
        # open because ``keep_alive`` is true.)
        
        if self.query_done() and not self.done:
            if self.finish_requested:
                self.close()  # this also sets self.done = True
            else:
                self.done = True  # channel may still be open but exit loop
    
    def close(self):
        """Trap the close event to ensure the ``done`` flag is set.
        """
        super(BaseCommunicator, self).close()
        self.done = True
    
    # Methods which must be implemented by derived classes
    
    def readable(self):
        """Return true if the channel is ready to read data.
        """
        raise NotImplementedError
    
    def writable(self):
        """Return true if there is data to be written.
        """
        raise NotImplementedError
    
    def run_loop(self, callback=None):
        """Run communication loop until self.query_done() is true.
        
        Allows callback function, which will run on each iteration
        of the loop; loop will also exit if the callback returns
        ``False`` (the specific object).
        """
        raise NotImplementedError
    
    # Methods which should be implemented in user code
    
    def process_data(self):
        """Do something with data received in ``self.read_data``.
        
        This method is called when a completed read is detected (the exact
        meaning of "completed read" depends on the specific data handling
        in use--it may be a terminator, a shutdown of the other end of the
        channel, etc.). The data received is in ``self.read_data`` while
        this method executes, but after that it will be erased, so if it
        needs to be stored, this method must put it somewhere else.
        """
        pass
