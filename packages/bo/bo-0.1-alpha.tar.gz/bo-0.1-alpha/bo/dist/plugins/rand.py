"""
Random operations like rolling a dice.

Commands:
    roll     -- roll a 6 sided dice
    roll a N -- roll an N-sided dice
"""
from random import Random

from bo.core.plugins import BasePlugin


text_listener = BasePlugin.text_listener
pattern_listener = BasePlugin.pattern_listener

class Plugin(BasePlugin):
    def __init__(self, bo, config, logger):
        super(Plugin, self).__init__(bo, config, logger)

        self.random = Random()

    @text_listener('roll')
    def roll6(self, message):
        message.reply(self.bo, '%s' % self.random.randrange(1, 7))
        return True

    @pattern_listener('roll a (?P<sides>[0-9]+)')
    def roll(self, message, sides):
        message.reply(self.bo, '%s' % self.random.randrange(1, int(sides)+1))
        return True
