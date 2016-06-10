import random

class Insult:
    def __init__(self, filename):
        self.insults = open(filename).read().splitlines()

    def get(self, victim_name):
        return random.choice(self.insults) % victim_name
