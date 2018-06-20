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
        self.spy_names = set()

    def message_react(self, decoded_text, decoded_username, *decoded_channels):
        normalized_own_username = normalize(self.username)
        normalized_text = normalize(decoded_text)
        if normalized_own_username in normalized_text:
            tokenized_normalized_text = normalized_text.split()
            if len(tokenized_normalized_text) > 1 and tokenized_normalized_text[0] == normalized_own_username and tokenized_normalized_text[1] == 'praise':
                self.say('No.', *decoded_channels)
            elif len(tokenized_normalized_text) > 1 and tokenized_normalized_text[0] == normalized_own_username and tokenized_normalized_text[1] == 'shrug':
                if ([normalize(token) for token in tokenized_normalized_text[2:]] == ['if', 'you', 'love', 'america']):
                    self.say('Meh.', *decoded_channels)
                else:
                    self.say('¯\_(ツ)_/¯', *decoded_channels)
            elif len(tokenized_normalized_text) > 3 and tokenized_normalized_text[0] == normalized_own_username and tokenized_normalized_text[2] == 'spy':
                action_name = tokenized_normalized_text[1]
                spy_name = decoded_text.split()[3]
                if action_name == 'reveal':
                    self.say('Revealing spy %s!' % spy_name, *decoded_channels)
                    self.spy_names.add(spy_name)
                elif action_name == 'conceal':
                    self.say('Concealing spy %s!' % spy_name, *decoded_channels)
                    self.spy_names.discard(spy_name)
            elif len(tokenized_normalized_text) > 2 and tokenized_normalized_text[0] == normalized_own_username and tokenized_normalized_text[1] == 'list' and tokenized_normalized_text[2] == 'spies':
                self.say('Spies:', *decoded_channels)
                for index, spy_name in enumerate(self.spy_names):
                    self.say('%s. %s' % (index + 1, spy_name), *decoded_channels)
            else:
                self.say(self.insult.get(decoded_username), *decoded_channels)

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

    def get_join_message(self):
        return 'I am here to help.'

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
