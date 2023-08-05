# -----------------------------------------------------------------------------
#    Shitman
#    Copyright (C) 2011  Sameer Rahmani <lxsameer@gnu.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------
import sys
from twisted.internet.protocol import Protocol, Factory


class Message(Protocol):
    """
    Message class represent the protocol the will be used for
    communicating with bot.
    """

    def __init__(self, factory):
        self.irc = factory

    def dataReceived(self, data):
        sys.stdout.write(data)
        self.transport.write(data)
        sys.stdout.write(self.irc.channel)

        self.irc.pinstance.say(self.irc.channel, data)


class UnixFactory(Factory):
    """
    Unix socket server. the run as a thread.
    """

    def __init__(self, tcpfactory):
        self.irc = tcpfactory

    def buildProtocol(self, addr):
        return Message(self.irc)
