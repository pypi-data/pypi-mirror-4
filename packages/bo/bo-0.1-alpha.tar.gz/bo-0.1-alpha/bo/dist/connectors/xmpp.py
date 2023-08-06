"""
Description:
    An XMPP connector.

Parameters:
    username -- The XMPP username
    password -- The XMPP password
    gtalk    -- Boolean, defaults to False. Specifies whether the connection
    is to Google Talk
    server   --
    port     --
"""
from __future__ import absolute_import
from threading import Thread
import sleekxmpp

from bo.core.connectors import BaseConnector, Message, User


class Connector(BaseConnector):
    def __init__(self, *args, **kwargs):
        super(Connector, self).__init__(*args, **kwargs)

        self.users_byjid = {}

        self.xmpp = sleekxmpp.ClientXMPP(
                self.config.get('username'), self.config.get('password'))
        self.xmpp.register_plugin('xep_0199') # XMPP Ping
        self.xmpp.add_event_handler("session_start", self._session_start)
        self.xmpp.add_event_handler("roster_update", self._roster_update)
        self.xmpp.add_event_handler("message", self._message)

    def _session_start(self, event):
        self.xmpp.send_presence()
        self.xmpp.get_roster()

    def _roster_update(self, roster):
        for jid in self.xmpp.client_roster:
            xmpp_user = self.xmpp.client_roster[jid]
            if not jid in self.users_byjid:
                user = User(connector=self, uid=jid, name=xmpp_user['name'])
                self.users_byjid[jid] = user
            self.users_byjid[jid].name = xmpp_user['name']

    def _message(self, message):
        if message['type'] in ('chat', 'normal'):
            self.signals.message_received.broadcast(
                message=Message(_from=self.users_byjid[message['from'].bare],
                                body=message['body']))

    def send_message(self, message):
        self.xmpp.send_message(mto=message['to'].uid,
                               mbody=message['body'],
                               mtype='chat')

    def connect(self):
        address = ()
        if self.config.get('gtalk', False):
            address = ('talk.google.com', 5222)
        elif self.config.get('server', False):
            address = (self.config['server'], self.config.get('port'))

        return self.xmpp.connect(address)

    def disconnect(self):
        self.xmpp.disconnect()

    def thread_target(self):
        self.xmpp.process(block=True)
