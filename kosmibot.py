import time
import unicodedata

from bot import Bot
from insult import Insult


class Kosmibot(Bot):
    def __init__(self, args):
        super().__init__(args)
        self.original_username = args.username
        self.ban_iteration = 1
        self.insult = Insult('insults.txt')

    def message_react(self, decoded_text, decoded_username, *decoded_channels):
        if normalize(self.username) in normalize(decoded_text):
            self.say(self.insult.get(decoded_username), *decoded_channels);

    def kick_react(self, decoded_username, *decoded_channels):
        self.join(*decoded_channels)
        self.say('Sorry, %s, I will try to be a better bot!' % decoded_username, *decoded_channels)

    def ban_react(self, decoded_username, *decoded_channels):
        self.disconnect()
        self.connect()
        self.username = self.original_username + str(self.ban_iteration)
        self.ban_iteration += 1
        self.identify()
        self.listen()

    def get_quit_message(self):
        return 'Am I a bad bot?'


def normalize(stri):
    return remove_marks(stri).lower()


def remove_marks(stri):
    return ''.join(remove_marks_char(c) for c in stri)


def remove_marks_char(char):
    try:
        return unicodedata.lookup(unicodedata.name(char).split(' WITH ', 1)[0])
    except (KeyError, ValueError):
        return char
