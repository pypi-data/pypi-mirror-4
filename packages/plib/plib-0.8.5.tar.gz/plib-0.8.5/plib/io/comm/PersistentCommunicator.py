#!/usr/bin/env python
"""
Module PersistentCommunicator
Sub-Package IO.COMM of Package PLIB
Copyright (C) 2008-2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the PersistentCommunicator class.
"""

from plib.stdlib.coll import fifo

from plib.io.base import BaseCommunicator


class PersistentCommunicator(BaseCommunicator):
    """Communicator class specialized for persistent I/O.
    
    Class for both client and server side communicators that want
    to maintain a persistent, full-duplex connection--i.e., instead
    of a write/read or read/write loop and then a check for done,
    always be ready to read, and write whenever you have something
    to write, and never being "done" by default (you have to explicitly
    call ``finish`` from inside the communication loop, or ``close``
    from outside it, to tell the loop that it is done). Expects
    a class earlier in the MRO to implement the ``start``,
    ``handle_read``, ``handle_write``, ``read_complete``,
    ``write_complete``, ``clear_read``, and ``clear_write`` methods;
    the intent is that this will be ``BaseData`` or a class derived
    from it.
    
    Note that, because reads and writes may overlap, this class also
    implements a simple queue for write data to ensure that all data
    gets written in the correct order and none is clobbered; to make this
    work, a class earlier in the MRO must also implement the ``start``
    method, which should enable the actual transfer of a single item of
    data. Also, the ``reading`` and ``writing`` fields are added to
    ensure that once a read or write is started, it must complete
    before another operation can start.
    """
    
    keep_alive = True  # must always close the channel explicitly
    
    data_queue = None
    reading = False
    writing = False
    
    def writable(self):
        # XXX: we could put the check for a deadlock (see ``start`` below;
        # basically when we have a data queue but nothing is pushed) here,
        # but testing with that configuration resulted in ``handle_write``
        # being called with *no* writable data (i.e., when this method
        # returned False!), which should not be possible. If that issue
        # could be figured out, we could alter the API for this class to
        # *not* require calling ``start`` to prime the write queue when
        # the class is first instantiated; instead, one could just have a
        # ``data_queue`` class member with an ordered list of initial data
        # items to be sent, and this method would automatically prime the
        # write queue. Since I'm not sure I want the API to be like that
        # anyway (I think I'd rather require calling ``start`` at least
        # once to prevent deadlock, and also allowing users to declare a
        # ``data_queue`` class field requires more checking to make sure
        # it's a fifo), I'm not going to bother trying to figure out the
        # above issue.
        return not (self.reading or self.write_complete() or self.done)
    
    def _push_next(self, data=None):
        # Push the next data item; we factor this out for easier coding
        # below, and to make clear that this communication model works
        # differently, by effectively re-naming the inherited ``start``
        # method to better describe what it now does. Note that no error
        # checking is done; this method should not be called from outside
        # the class.
        if not data:
            data = self.data_queue.next()
        super(PersistentCommunicator, self).start(data)
    
    def start(self, data):
        # We check ``self.data_queue`` here to ensure that we don't
        # inadvertently send data out of order (i.e., even if there is
        # no currently scheduled write data, we append to the queue if
        # it is non-empty). This should never actually happen because
        # ``self.write_complete`` should only return ``True`` here if
        # the queue is empty (since the ``handle_write`` method will
        # automatically push the next queue item to be written, making
        # ``self.write_complete`` false--see the comment there). The
        # opposite risk which is introduced by this check here, that
        # we could end up in a deadlock situation where there is data
        # in the queue but it never gets pushed, is prevented by the
        # ``write_complete`` check below.
        if self.write_complete() and not self.data_queue:
            self._push_next(data)
        else:
            if self.data_queue is None:
                self.data_queue = fifo()
            self.data_queue.append(data)
            # This check handles the case where we had a data queue but
            # nothing was actually pushed; we couldn't just push the data
            # this method was called with because it belongs at the end of
            # the queue, but we have to push *something* or we'll just stay
            # in our do_loop forever and never send anything.
            if self.write_complete():
                self._push_next()
    
    def handle_write(self):
        self.writing = True
        super(PersistentCommunicator, self).handle_write()
        if self.write_complete():
            self.clear_write()
            self.check_done()
            self.writing = False
            # NOTE: We automatically push the next data item in the queue
            # here, which should make ``self.write_complete`` return
            # ``False`` again (it had to return ``True`` to get us here via
            # the ``if`` statement). Since ``write_complete`` had to be
            # ``False`` to enter this method in the first place (because
            # ``writable`` will only return ``True`` if ``write_complete``
            # returns ``False``, and this method can only be entered if
            # ``writable`` is ``True; ``write_complete`` would have been made
            # ``True`` by this point by what happened in the super call
            # above, if we get here), this code should make it impossible
            # for ``write_complete`` to be seen as ``False`` anywhere outside
            # of the above ``if`` statement unless the data queue is empty.
            # Thus, the check of the queue in ``start`` above should not,
            # strictly speaking, be necessary; we put it in only because I'm
            # paranoid enough to think that there might be a way I haven't
            # thought of.
            if (not self.done) and self.data_queue:
                self._push_next()
    
    def readable(self):
        return not (self.writing or self.done)
    
    def handle_read(self):
        self.reading = True
        super(PersistentCommunicator, self).handle_read()
        if self.read_complete():
            self.process_data()
            self.clear_read()
            self.check_done()
            self.reading = False
