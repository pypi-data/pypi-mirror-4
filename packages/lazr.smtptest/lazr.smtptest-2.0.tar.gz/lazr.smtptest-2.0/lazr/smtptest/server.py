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

"""The SMTP test server."""

from __future__ import absolute_import, print_function, unicode_literals


__metaclass__ = type
__all__ = [
    'QueueServer',
    'Server',
    ]


import smtpd
import socket
import logging
import asyncore

try:
    from queue import Empty
except ImportError:
    # Python 2
    from Queue import Empty

from email import message_from_string


COMMASPACE = ', '
log = logging.getLogger('lazr.smtptest')


class Channel(smtpd.SMTPChannel):
    """A channel that can reset the mailbox."""

    def __init__(self, server, connection, address):
        self._server = server
        smtpd.SMTPChannel.__init__(self, server, connection, address)

    def smtp_EXIT(self, argument):
        """EXIT - a new SMTP command to cleanly stop the server."""
        self.push('250 Ok')
        self._server.stop()

    def smtp_RSET(self, argument):
        """RSET - hijack this to reset the server instance."""
        self._server.reset()
        smtpd.SMTPChannel.smtp_RSET(self, argument)

    def send(self, data):
        """See `SMTPChannel.send()`."""
        # Call the base class's send method, but catch all socket errors since
        # asynchat/asyncore doesn't do it.
        try:
            return smtpd.SMTPChannel.send(self, data)
        except socket.error:
            # Nothing here can affect the outcome.
            pass

    def add_channel(self, map=None):
        # This has an old style base class.  We want to make _map equal to
        # our server's socket_map, to make this thread safe with other
        # asyncores.  We do it here, overriding the behavior of the asyncore
        # __init__ as soon as we can, without having to copy over code from
        # the rest of smtpd.SMTPChannel.__init__ and modify it.
        if self._map is not self._server.socket_map:
            self._map = self._server.socket_map
        smtpd.SMTPChannel.add_channel(self, map)


class Server(smtpd.SMTPServer):
    """An SMTP server."""

    def __init__(self, host, port):
        """Create an SMTP server.

        :param host: The host name to listen on.
        :type host: str
        :param port: The port to listen on.
        :type port: int
        """
        self.host = host
        self.port = port
        self.socket_map = {}
        smtpd.SMTPServer.__init__(self, (host, port), None)
        self.set_reuse_addr()
        log.info('[SMTPServer] listening: %s:%s', host, port)

    def add_channel(self, map=None):
        # This has an old style base class.  We want to make _map equal to
        # socket_map, to make this thread safe with other asyncores.  We do
        # it here, overriding the behavior of the SMTPServer __init__ as
        # soon as we can, without having to copy over code from the rest of
        # smtpd.SMTPServer.__init__ and modify it.
        if self._map is not self.socket_map:
            self._map = self.socket_map
        smtpd.SMTPServer.add_channel(self, map)

    def handle_accept(self):
        """Handle connections by creating our own Channel object."""
        connection, address = self.accept()
        log.info('[SMTPServer] accepted: %s', address)
        Channel(self, connection, address)

    def process_message(self, peer, mailfrom, rcpttos, data):
        """Process a received message."""
        log.info('[SMTPServer] processing: %s, %s, %s, size=%s',
                 peer, mailfrom, rcpttos, len(data))
        message = message_from_string(data)
        message['X-Peer'] = '%s:%s' % (peer[0], peer[1])
        message['X-MailFrom'] = mailfrom
        message['X-RcptTo'] = COMMASPACE.join(rcpttos)
        self.handle_message(message)
        log.info('[SMTPServer] processed message: %s',
                 message.get('message-id', 'n/a'))

    def start(self):
        """Start the asyncore loop."""
        log.info('[SMTPServer] starting asyncore loop')
        asyncore.loop(map=self.socket_map)

    def stop(self):
        """Stop the asyncore loop."""
        asyncore.close_all(map=self.socket_map)
        self.close()

    def reset(self):
        """Do whatever you need to do on a reset."""
        log.info('[SMTPServer] reset')

    def handle_message(self, message):
        """Handle the received message.

        :param message: the completed, parsed received email message.
        :type message: `email.message.Message`
        """
        pass


class QueueServer(Server):
    """A server which puts messages in a queue."""

    def __init__(self, host, port, queue):
        """Create an SMTP server which puts messages in a queue.

        :param host: The host name to listen on.
        :type host: str
        :param port: The port to listen on.
        :type port: int
        :param queue: The queue to put messages in.
        :type queue: object with a .put() method taking a single message
            object.
        """
        Server.__init__(self, host, port)
        self.queue = queue

    def handle_message(self, message):
        """See `Server.handle_message()`."""
        self.queue.put(message)

    def reset(self):
        """See `Server.reset()`."""
        while True:
            try:
                self.queue.get_nowait()
            except Empty:
                break
