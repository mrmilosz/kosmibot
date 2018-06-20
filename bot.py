import errno
import socket
import ssl
import time

from log import log


class Bot:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.channels = args.channels
        self.username = args.username
        self.realname = args.realname

    def start(self):
        while True:
            try:
                self.connect()
                self.identify()
                self.listen()
                break
            except socket.error as e:
                self.handle_error(e)
                self.disconnect()

    def stop(self, signum, frame):
        self.quit()

    def connect(self):
        self.irc = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.irc.connect((self.host, self.port))

    def identify(self):
        self.send('NICK %s' % self.username)
        self.send('USER %s 0 * :%s' % (self.username, self.realname))

    def listen(self):
        data_buffer = b''
        while True:
            data = self.irc.recv(4096)
            if len(data) == 0:
                break

            lines = data.split(b'\r\n')
            lines[0] = data_buffer + lines[0]
            data_buffer = lines.pop()

            for message in lines:
                log('SERVER: %s' % message.decode('utf8', 'replace'))
                self.handle_message(message)

    def disconnect(self):
        self.irc.close()
        self.irc = None

    def handle_message(self, message):
        command, tail = get_token(message)

        if command == b'PING':
            ident, tail = get_token(tail)
            if ident is not None:
                self.send('PONG :%s' % ident.lstrip(b':').decode('utf8', 'ignore'))
            else:
                self.send('PONG')

        elif command.startswith(b':'):
            source = command.lstrip(b':')
            command, tail = get_token(tail)

            decoded_username = source.split(b'!', 1)[0].decode('utf8', 'ignore')

            if command == b'001':
                self.join(self.channels) # TODO make self.channels a list, not a comma-separated string

            elif command == b'474':
                target, tail = get_token(tail)
                channel, tail = get_token(tail)
                decoded_channel = channel and channel.decode('utf8', 'ignore')
                self.ban_react(decoded_username, decoded_channel)

            elif command == b'KICK':
                channel, tail = get_token(tail)
                decoded_channel = channel and channel.decode('utf8', 'ignore')
                target, tail = get_token(tail)
                decoded_target = target and target.decode('utf8', 'ignore')

                if decoded_target == self.username:
                    self.kick_react(decoded_username, decoded_channel)

            elif command == b'PRIVMSG':
                if decoded_username != self.username:
                    channel, tail = get_token(tail)
                    if channel and channel.startswith(b'#'):
                        decoded_channel = channel.decode('utf8', 'ignore')
                    else:
                        decoded_channel = decoded_username
                    text = tail.lstrip(b':')

                    try:
                        decoded_text = text.decode('utf8', 'strict')
                    except UnicodeError:
                        decoded_text = text.decode('latin1', 'ignore')

                    self.message_react(decoded_text, decoded_username, decoded_channel)

    def message_react(self, decoded_text, decoded_username, *decoded_channels):
        pass

    def kick_react(self, decoded_username, *decoded_channels):
        pass

    def ban_react(self, decoded_username, *decoded_channels):
        pass

    def get_quit_message(self):
        return 'Leaving.'

    def get_quit_message(self):
        return None

    def handle_error(self, e):
        log(e)
        if e.errno == errno.ECONNRESET:
            time.sleep(1)
        else:
            time.sleep(300)

    def join(self, *decoded_channels):
        self.send('JOIN %s' % ','.join(decoded_channels))
        join_message = self.get_join_message()
        if join_message is not None:
            self.say(join_message, *decoded_channels)

    def say(self, decoded_text, *decoded_channels):
        self.send('PRIVMSG %s :%s' % ('.'.join(decoded_channels), decoded_text))

    def send(self, decoded_message):
        self.irc.send(('%s\r\n' % decoded_message).encode('utf8'))
        log('CLIENT: %s' % decoded_message)

    def quit(self):
        self.send('QUIT :%s' % self.get_quit_message())


def get_token(bts):
    if bts is None:
        return (None, None)
    tokens = bts.split(None, 1)
    return tuple(tokens) if len(tokens) == 2 else (tokens[0], None)
