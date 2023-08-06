import argparse

from twisted.internet import reactor

from ircbot import IRCBotFactory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=6667)
    parser.add_argument('-n', '--nick', type=str, default='bot')
    parser.add_argument('channels', nargs='+')

    args = parser.parse_args()

    reactor.connectTCP(
        args.host, int(args.port),
        IRCBotFactory(
            ('#{}'.format(c) for c in args.channels),
            nickname=args.nick
        )
    )
    reactor.run()
