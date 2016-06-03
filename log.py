import datetime


def get_timestamp():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def log(*messages):
    print('%s %s' % (get_timestamp(), ''.join('[%s]' % message for message in messages)))
