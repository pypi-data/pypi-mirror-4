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
import time
import logging

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from server import UnixFactory


class LogBot(irc.IRCClient):
    """
    A logging IRC bot.
    """

    nickname = "Pman"
    commands = {}
    help_string = [
        "help\t\t\tPrint out this message.",
        ]

    def __init__(self, factory, nickname):
        self.factory = factory
        self.nickname = nickname

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = logging.getLogger()
        self.logger.log(50, "[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log(50, "[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))

    # callbacks for events
    def signedOn(self):
        """
        Called when bot has succesfully signed on to server.
        """
        self.join(self.factory.channel)

    def joined(self, channel):
        """
        This will get called when the bot joins the channel.
        """
        self.logger.log(50, "[I have joined %s]" % channel)
        self.say(channel, "Hi all, %s is here." % self.nickname)

    def privmsg(self, user, channel, msg_):
        """
        This will get called when the bot receives a message.
        """
        user = user.split('!', 1)[0]
        self.logger.log(50, "<%s> %s" % (user, msg_))

        # Otherwise check to see if it is a message directed at me
        if msg_.startswith(self.nickname):
            msg = ""
            command, internal, args = self.find_command(msg_)
            if not command:
                msg = "%s: %s" % (user,
                                  "Commant not found. try \"help\".")
            else:
                if internal:
                    result = command(user, channel,
                                     *args)
                else:
                    result = command(self, user, channel,
                                     *args)

                if result:
                    msg = "%s: %s" % (user, result)
                else:
                    self.logger.log(50, "<%s> %s" % (
                        self.nickname, msg))
                    return

            if channel == self.nickname:
                self.msg(user, msg)
            else:
                self.msg(channel, msg)

            self.logger.log(50, "<%s> %s" % (self.nickname, msg))

    def find_command(self, msg):
        """
        Find the handler of command mentioned in msg.
        """
        internal = 0
        parsed_msg = msg.split(" ")
        if parsed_msg[0].startswith(self.nickname):
            parsed_msg.pop(0)
        command = parsed_msg.pop(0)
        command = command.strip()
        func = None
        if command in self.commands:
            func = self.commands[command]
        else:
            func = getattr(self, "command_%s" % command, None)
            internal = 1

        if not func:
            return None, internal, []
        return func, internal, parsed_msg

    def action(self, user, channel, msg):
        """
        This will get called when the bot sees someone do an action.
        """
        user = user.split('!', 1)[0]
        self.logger.log(50, "* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """
        Called when an IRC user changes their nickname.
        """
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log(50, "%s is now known as %s" % (old_nick, new_nick))

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '_'

    # Commands -------------------------------------
    def command_help(self, user, channel, *args):
        """
        Print out help.
        """
        msg = []
        append = msg.append
        for command in self.commands:
            append(command.__doc__)

        output = "%s%s" % ("\r\n".join(self.help_string),
                           "\n".join(msg))
        self.msg(user, output)
        return None


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = LogBot

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

    def buildProtocol(self, addr):
        self.pinstance = LogBot(self, self.nickname)
        return self.pinstance
