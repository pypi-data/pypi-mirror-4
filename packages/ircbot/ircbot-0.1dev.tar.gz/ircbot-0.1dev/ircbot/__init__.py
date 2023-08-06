import re

from twisted.words.protocols import irc
from twisted.internet import protocol


class IRCBot(irc.IRCClient):
    @property
    def nickname(self):
        return self.factory.nickname

    def signedOn(self):
        for c in self.factory.channels:
            self.join(c)
        print('signed on as {}.'.format(self.nickname))

    def joined(self, channel):
        print('joined {}'.format(channel))

    def privmsg(self, user, channel, msg):
        """ deals with messages, both private and public, in a channel

            Your code will most likely go in here.
        """
        username = user.split('!', 1)[0]
        if channel == self.nickname:
            self.msg(username, "whisper back ...")
        if self.nickname in msg:
            msg = self.factory.nick_stripper.sub('', msg)
            self.msg(channel, 'echo: {}'.format(msg))


class IRCBotFactory(protocol.ClientFactory):
    protocol = IRCBot

    def __init__(self, channels, nickname='bot'):
        self.channels = channels
        self.nickname = nickname
        self.nick_stripper = re.compile(r'{}\s*?\:?'.format(self.nickname))

    def clientConnectionLost(self, connector, reason):
        print('lost connection({}), reconnecting.'.format(reason))

    def clientConnectionFailed(self, connector, reason):
        print('could not connect: {}'.format(reason))
