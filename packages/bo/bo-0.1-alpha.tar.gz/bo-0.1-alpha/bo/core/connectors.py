from threading import Thread, Event

from bo.dispatch import Signal


class User(object):
    def __init__(self, connector, uid, name):
        self.connector = connector
        self.uid = uid
        self.name = name


class Message(object):
    available_attribs = set(['from', 'to', 'body'])

    def __init__(self, **kwargs):
        provided_attribs = dict(kwargs)
        if '_from' in provided_attribs:
            provided_attribs['from'] = provided_attribs['_from']
            provided_attribs.pop('_from')

        invalid_attribs = set(provided_attribs.keys()) - self.available_attribs
        if invalid_attribs:
            raise AttributeError('Invalid attributes %s' % invalid_attribs)

        self.attribs = dict(provided_attribs)

    def __getitem__(self, key):
        if key in self.attribs:
            return self.attribs[key]
        raise KeyError(key)

    def reply(self, bo, text):
        bo.send_text(self['from'], text)


class _Bunch(object):
    def __init__(self, **stuff):
        self.__dict__.update(**stuff)


class BaseConnector(object):
    def __init__(self, bo, config):
        self.bo = bo
        self.config = config
        self.name = config['name']

        self.signals = _Bunch(
            message_received=Signal('connector:message_received',
                                    receiving_args=['message']))
        self.thread = Thread(name='thread/%s' % self.name,
                             target=self.thread_target)

    def thread_target(self):
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def work(self):
        self.thread.start()

    def is_working(self):
        return self.thread.isAlive()

    def is_working(self):
        return self.thread.isAlive()

    def join(self, timeout):
        self.thread.join(timeout)

    def send_message(self, to, message):
        raise NotImplementedError()
