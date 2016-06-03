#!/usr/bin/env python3

import argparse
import signal
import sys

from kosmibot import Kosmibot
from log import log


def main():
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='An IRC bot.')
        parser.add_argument('--host'     , default='irc.quakenet.org' , type=str , help='the IRC server to which to connect')
        parser.add_argument('--port'     , default=6667               , type=int , help='the port on which to connect')
        parser.add_argument('--channels' , default='#kosmibot-test'   , type=str , help='the channel(s) to join')
        parser.add_argument('--username' , default='kosmibot'         , type=str , help='the username that the bot will use')
        parser.add_argument('--realname' , default='KosmiBot'         , type=str , help='the WHOIS name for the bot')
        args = parser.parse_args()

        bot = Kosmibot(parser.parse_args())
        signal.signal(signal.SIGINT, bot.stop)
        bot.start()

    except Exception as e:
        log(e)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
