"""
Gives an one line desciption of how long the system has been running.

Commands:
    uptime -- Tell how long the system has benn running
"""
from time import time, strftime

from bo.core.plugins import BasePlugin


text_listener = BasePlugin.text_listener

class Plugin(BasePlugin):
    def __init__(self, bo, config, logger):
        super(Plugin, self).__init__(bo, config, logger)

        self.started_time = int(time())

    @text_listener('uptime')
    def uptime(self, message):
        seconds = int(time()) - self.started_time

        days = seconds / (24 * 60 * 60)
        seconds = seconds % (24 * 60 * 60)

        multiples = [60 * 60, 60]
        segments = []
        for m in multiples:
            segment, seconds = divmod(seconds, m)
            segments.append(str(segment).zfill(2))
        nice_time = ':'.join(segments)

        message.reply(
            self.bo,
            '%s up %s day(s), %s' % (strftime('%H:%M:%S'), days, nice_time))
        return True
