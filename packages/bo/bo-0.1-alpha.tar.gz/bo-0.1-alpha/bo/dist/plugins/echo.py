"""
Echoes whatever is said.
"""
from bo.core.plugins import BasePlugin


class Plugin(BasePlugin):
    def __init__(self, bo, config, logger):
        super(Plugin, self).__init__(bo, config, logger)
        self.bo.listening_signals.message_received.connect(
            receiver=self.echo)

    def echo(self, message, **args):
        message.reply(self.bo, message['body'])
        return True
