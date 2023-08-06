from __future__ import with_statement
import logging

from bo.dispatch import Signal
from bo.core.connectors import Message


def _getChild(logger, childName):
    return logging.getLogger('.'.join([logger.name, childName]))
get_child_logger = getattr(logging.Logger, 'getChild', _getChild)


class _Bunch(object):
    def __init__(self, **stuff):
        self.__dict__.update(**stuff)


class Bo(object):
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

        self.connectors = []
        self.plugins = []
        self.listening_signals = _Bunch(
            message_received = Signal('bo:listening_message_received', logger=self.logger))
        self.signals = _Bunch(
            message_received = Signal('bo:message_received'))

        # load the connectors
        for connector_config in self.config['connectors']:
            try:
                connector_class = __import__(connector_config['type'],
                                             fromlist=['Connector']).Connector
            except ImportError:
                self.logger.exception(
                    'Could not load connector %(type)s/%(name)s',
                    connector_config)
                continue

            try:
                connector = connector_class(self, connector_config)
            except StandardError:
                self.logger.exception(
                    'Could not create the connector from %(type)s/%(name)s',
                    connector_config)
                continue

            connector.signals.message_received.connect(
                self._on_connector_message_received)

            if not connector.connect():
                self.logger.error(
                    'Connector %(type)s/%(name)s could not connect',
                    connector_config)
                continue
            self.connectors.append(connector)

        # load the plugins
        for plugin_name in self.config['plugins']:
            try:
                plugin_class = __import__(plugin_name,
                                          fromlist=['Plugin']).Plugin
            except StandardError:
                self.logger.exception('Could not load plugin %s', plugin_name)
                continue

            try:
                plugin = plugin_class(self, {}, self.logger)
            except StandardError:
                self.logger.exception('Could not initialize plugin %s',
                                      plugin_name)
                continue
            self.plugins.append(plugin)
            self.logger.info('Loaded plugin %s', plugin_name)

        for c in self.connectors:
            c.work()

    def work_forever(self):
        for c in self.connectors:
            self.logger.debug('Waiting on %(type)s/%(name)s', c.config)
            while c.is_working():
                c.join(1)

    def close(self):
        for c in self.connectors:
            c.disconnect()

        for p in self.plugins:
            p.close()
        self.logger.info('Bye bye')

    def send_text(self, to, text):
        return self.send_message(Message(to=to, body=text))

    def send_message(self, message):
        return message['to'].connector.send_message(message)

    def _on_connector_message_received(self, **signal_args):
        self.logger.debug('_on_message_received %s', signal_args)
        self.listening_signals.message_received.send_robust(
            message=signal_args['message'])
