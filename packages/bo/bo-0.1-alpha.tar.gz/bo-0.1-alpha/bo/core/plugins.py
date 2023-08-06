from inspect import getmembers, ismethod
import re


class BasePlugin(object):
    LISTENERS_ATTR = '__bo_listeners'

    def __init__(self, bo, config, logger):
        self.bo = bo
        self.config = config
        self.logger = logger

        self._receivers = []
        for (_, method) in getmembers(self, predicate=ismethod):
            listeners = getattr(method, self.LISTENERS_ATTR, [])
            for (partial_receiver, mesg_filter) in listeners:
                def create_receiver(partial_receiver, method):
                    return lambda **args: partial_receiver(method, **args)
                def create_signals_filter(mesg_filter):
                    return lambda **args: mesg_filter(args['message'])

                signal = self.bo.listening_signals.message_received
                receiver = create_receiver(partial_receiver, method)
                signal.connect(receiver,
                               create_signals_filter(mesg_filter),
                               weak=False)
                self._receivers.append((signal, receiver))

    def close(self):
        for (signal, receiver) in self._receivers:
            signal.disconnect(receiver)

    @classmethod
    def _register_listener(cls, unbound_method, partial_receiver, mesg_filter):
        """ A helper class for creating listener decorators. """
        listeners = getattr(unbound_method, cls.LISTENERS_ATTR, None)
        if listeners is None:
            listeners = []
            setattr(unbound_method, cls.LISTENERS_ATTR, listeners)

        listeners.append((partial_receiver, mesg_filter))

    @classmethod
    def text_listener(cls, text, ignorecase=True):
        def wrap(unbound_method):
            if ignorecase:
                match_text = text.lower()
                msg_filter = lambda msg: msg['body'].lower() == match_text
            else:
                match_text = text
                msg_filter = lambda msg: msg['body'] == match_text

            partial_receiver = lambda method, **args: method(args['message'])
            cls._register_listener(unbound_method,
                                   partial_receiver,
                                   msg_filter)
            return unbound_method
        return wrap

    @classmethod
    def question_listener(cls, text, ignorecase=True):
        return cls.text_listener(text + '?', ignorecase)

    @classmethod
    def pattern_listener(cls, pattern, ignorecase=True):
        def wrap(unbound_method):
            flags = re.IGNORECASE if ignorecase else 0
            regex = re.compile(pattern, flags)
            def partial_receiver(method, **args):
                match = regex.search(args['message']['body'])
                if not match:
                    return False
                return method(args['message'], **match.groupdict())
            cls._register_listener(unbound_method,
                                   partial_receiver,
                                   lambda mesg: True)
            return unbound_method
        return wrap
