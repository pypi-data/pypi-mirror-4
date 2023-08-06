"""
Description:
    A simple (test) connector to chat with the bot via the console.
"""
from threading import Event
from sys import stdout

from bo.core.connectors import BaseConnector, Message, User


class Connector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super(Connector, self).__init__(*args, **kwargs)

        self.disconnect_event = Event()

    def connect(self):
        print '-', 'Connected'
        return True

    def disconnect(self):
        print '-', 'Close'
        self.disconnect_event.set()

    def thread_target(self):
        user = User(name='user', uid='uid', connector=self)
        try:
            stdout.flush()
            while not self.disconnect_event.isSet():
                line = raw_input('> ')
                self.signals.message_received.broadcast(
                    message=Message(_from=user,
                                    body=line))
            print '>',
        except EOFError:
            print

    def send_message(self, message):
        print
        print '<', message['body']
        print '> ',
        stdout.flush()
