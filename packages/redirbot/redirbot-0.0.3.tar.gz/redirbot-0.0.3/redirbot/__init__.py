from ConfigParser import SafeConfigParser
import argparse

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import sys
from datetime import datetime

class Logger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def msg(self, message):
        """Write a message to the file."""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class RedirBot(irc.IRCClient):
    def __init__(self, nick):
        self.nickname = nick

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.logger.msg("connected")

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.factory.logger.msg("disconnected")

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for i in self.factory.channels:
            self.join(i)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.factory.logger.msg("joined %s" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.factory.logger.msg("[%s] <%s> %s" % (channel, user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname or \
            msg.startswith(self.nickname + ":"):
                msg = "The user you are trying to reach is known under " \
                "nickname %s" % self.factory.nickname_user
                self.msg(user, msg)
                self.factory.logger.msg("[%s] <%s> %s" % (user, self.nickname, msg))
                return

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.factory.logger.msg("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.factory.logger.msg("%s is now known as %s" % (old_nick, new_nick))

    def userRenamed(self, old_nick, new_nick):
        self.nickFreed(old_nick)

    def nickFreed(self, nick):
        if nick == self.factory.nickname:
            self.setNick(self.factory.nickname)

    def userQuit(self, nick, quitMessage):
        self.nickFreed(nick)

    def sendLine(self, line):
        self.factory.rawlogger.msg("-> %s" % line)
        irc.IRCClient.sendLine(self, line)

    def lineReceived(self, line):
        self.factory.rawlogger.msg("<- %s" % line)
        irc.IRCClient.lineReceived(self, line)

class BotFactory(protocol.ReconnectingClientFactory):
    maxDelay = 15 * 60

    def __init__(self, nickname, nickname_user, channels, filename, filename_raw):
        self.nickname = nickname
        self.channels = channels
        self.filename = filename
        self.filename_raw = filename_raw
        self.nickname_user = nickname_user

    def buildProtocol(self, addr):
        p = RedirBot(self.nickname)
        p.factory = self
        return p

    def startFactory(self):
        self.rawlogger = Logger(open(self.filename_raw, "a"))
        self.logger = Logger(open(self.filename, "a"))
        self.logger.msg(self.channels)

    def stopFactory(self):
        self.factory.logger.close()
        self.rawlogger.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str,
        help='config file')
    args = parser.parse_args()

    cp = SafeConfigParser()
    cp.read(args.config)
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    bot_cnf = {
        'nickname': cp.get("main","nickname_bot"),
        'nickname_user': cp.get("main", "nickname_user"),
        'channels': cp.get("main", "channels").split(" "),
        'filename': cp.get("main", "logfile"),
        'filename_raw': cp.get("main", "logfile_raw"),
    }

    f = BotFactory(**bot_cnf)
    reactor.connectTCP(cp.get("server", "host"), cp.getint("server", "port"), f)
    reactor.run()
