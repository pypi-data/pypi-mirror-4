# Copyright 2009-2013 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.smtptest
#
# lazr.smtptest is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.smtptest is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.smtptest.  If not, see <http://www.gnu.org/licenses/>.

"""The SMTP test controller."""

from __future__ import absolute_import, print_function, unicode_literals


__metaclass__ = type
__all__ = [
    'Controller',
    'QueueController',
    ]


import logging
import smtplib
import threading

try:
    from queue import Empty, Queue
except ImportError:
    # Python 2
    from Queue import Empty, Queue

from lazr.smtptest.server import QueueServer


log = logging.getLogger('lazr.smtptest')


class Controller:
    """The SMTP server controller."""

    def __init__(self, server):
        """The controller of the SMTP server.

        :param server: The SMTP server to run.  The server must have `host`
            and `port` attributes set.
        :type server: `lazr.smtptest.server.Server` or subclass
        """
        self._server = server
        self._thread = threading.Thread(target=server.start)
        self._thread.daemon = True

    def _connect(self):
        """Connect to the SMTP server running in the thread.

        :return: the connection to the SMTP server
        :rtype: `smtplib.SMTP`
        """
        smtpd = smtplib.SMTP()
        smtpd.connect(self._server.host, self._server.port)
        return smtpd

    def start(self):
        """Start the SMTP server in a thread."""
        log.info('starting the SMTP server thread')
        self._thread.start()
        # Wait until the server is actually responding to clients.
        log.info('connecting to %s:%s', self._server.host, self._server.port)
        smtpd = self._connect()
        response = smtpd.helo('test.localhost')
        log.info('Got HELO response: %s', response)
        smtpd.quit()

    def stop(self):
        """Stop the smtp server thread."""
        log.info('stopping the SMTP server thread')
        smtpd = self._connect()
        smtpd.docmd('EXIT')
        # Wait for the thread to exit.
        self._thread.join()
        log.info('SMTP server stopped')

    def reset(self):
        """Sent a RSET to the server."""
        log.info('resetting the SMTP server.')
        smtpd = self._connect()
        smtpd.docmd('RSET')


class QueueController(Controller):
    """An SMTP server controller that coordinates through a queue."""

    def __init__(self, host, port):
        """The controller which coordinates via a Queue.

        :param host: The host name to listen on.
        :type host: str
        :param port: The port to listen on.
        :type port: int
        """
        self.queue = Queue()
        self.server = None
        self._make_server(host, port)
        super(QueueController, self).__init__(self.server)

    def _make_server(self, host, port):
        """Create the server instance, storing it on `self.server`.

        This interface is non-public; it is for subclasses that need to
        override server instantiation.

        :param host: The host name to listen on.
        :type host: str
        :param port: The port to listen on.
        :type port: int
        """
        self.server = QueueServer(host, port, self.queue)

    def __iter__(self):
        """Iterate over all the messages in the queue."""
        while True:
            try:
                yield self.queue.get_nowait()
            except Empty:
                raise StopIteration
