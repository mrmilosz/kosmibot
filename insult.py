import random

class Insult:
    def __init__(self, filename):
        self.insults = open(filename).read().splitlines()

    def get(self, victim_name):
        insult_format = random.choice(self.insults)
        return insult_format % victim_name if insult_format.count('%s') == 1 else insult_format
