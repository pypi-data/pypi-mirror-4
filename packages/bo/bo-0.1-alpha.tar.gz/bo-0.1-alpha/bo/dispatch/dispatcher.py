from __future__ import with_statement
import weakref
import threading

from bo.dispatch import saferef


class _DummyLogger(object):
    def debug(self, *args):
        pass

    def info(self, *args):
        pass

    def warn(self, *args):
        pass

    def error(self, *args):
        pass

    def exception(self, *args):
        pass


WEAKREF_TYPES = (weakref.ReferenceType, saferef.BoundMethodWeakref)

class Signal(object):
    def __init__(self, name, receiving_args=None, logger=None):
        """ Creates a signal.

        Keyword arguments:
        receiving_args -- A list of arguments that the signal might pass along
        with the signal.
        """
        self.name = name
        if receiving_args is None:
            receiving_args = []
        self.receiving_args = set(receiving_args)
        self.logger = logger or _DummyLogger()
        self.receivers = []
        self.lock = threading.Lock()

    def connect(self, receiver,
            signals_filter=lambda **kw: True, weak=True):
        """ Connect receiver to this signal.

        Keyword arguments:
        receiver -- The function or another callable to receive the signal. It
        must be able to receive keyword arguments. If weak is True, receiver
        must be weak referencable by saferef.safeRef.
        signals_filter -- A function or another callable to decide whether to
        call receiver on signal using 
        weak -- Whether to use a weak reference to store a reference to
        receiver.
        In most of the cases, weak references is the best choice, but when
        passing a temporary object (lambda **args: True), weak=False is needed
        because the lambda object is to be garbage collected after the call.
        """
        self.logger.debug('%s.connect %s weak=%s', self.name, receiver, weak)
        
        if weak:
            receiver = saferef.safeRef(receiver,
                                       onDelete=self._remove_receiver)
        with self.lock:
            if not any(r == receiver for r, _ in self.receivers):
                self.receivers.append((receiver, signals_filter))

    def disconnect(self, receiver):
        """ Disconnect a receiver from this signal.

        Keyword arguments:
        receiver -- The registered receiver to disconnect.
        """
        self.logger.debug('%s.disconnect %s', self.name, receiver)

        with self.lock:
            for index, (r, _) in enumerate(self.receivers):
                if r == receiver:
                    del self.receivers[index]
                    break

    def broadcast(self, **args):
        """ Send signal to all receivers connected.

        Keyword arguments:
        args -- Passed to each receiver.
        
        Returns a list of tuples [(receiver, response), ...]

        All exceptions are left unhandled, so any exceptions thrown are
        propagated to the caller of broadcast(), thus terminating the
        broadcast. As a result, some or all receivers may not get the signal.
        To prevent this, use broadcast_robust().
        """
        self.logger.debug('%s.broadcast', self.name)

        responses = []
        for receiver, signals_filter in self._live_receivers():
            if signals_filter(**args):
                responses.append((receiver, receiver(signal=self, **args)))
        return responses

    def broadcast_robust(self, **args):
        """ Send signal to all receivers connected.

        Keyword arguments:
        args -- Passed to each receiver.
        
        Returns a list of tuples [(receiver, response), ...]

        In contrast to broadcast(), exceptions are caught. If a receiver raises
        an exception, the exception as a response from the receiver.
        """
        self.logger.debug('%s.broadcast_robust', self.name)

        responses = []
        for (receiver, signals_filter) in self._live_receivers():
            if signals_filter(**args):
                try:
                    response = receiver(signal=self, **args)
                except Exception, err:
                    response = err
                responses.append((receiver, response))
        return responses

    def send(self, **args):
        """ Send signal to all receivers connected, until a receiver handles
        the signal. If a receiver accepts a signal, it should return a true
        value.

        Keyword arguments:
        args -- Passed to each receiver.

        Returns the response from the receiver that handled the signal. If no
        receiver handled the signal, False is returned.

        All exceptions are left unhandled, so any exceptions thrown are
        propagated to the caller of send(), thus terminating the sending.
        As a result, some or all receivers may not get the signal. To prevent
        this, use send_robust().
        """
        self.logger.debug('%s.send', self.name)

        for (receiver, signals_filter) in self._live_receivers():
            if signals_filter(**args):
                response = receiver(signal=self, **args)
                if response:
                    return (receiver, response)
        return False

    def send_robust(self, **args):
        """ Send signal to all receivers connected, until a receiver handles
        the signal. If a receiver accepts a signal, it should return a true
        value.

        Keyword arguments:
        args -- Passed to each receiver.
        
        Returns the response from the receiver that handled the signal. If no
        receiver handled the signal, False is returned.

        In contrast to send(), exceptions are caught. If a receiver raises
        an exception, the exception as a response from the receiver.
        """
        self.logger.debug('%s.send_robust', self.name)

        for (receiver, signals_filter) in self._live_receivers():
            if signals_filter(**args):
                try:
                    response = receiver(signal=self, **args)
                    self.logger.debug('%s.send_robust %s %s %s', self.name, receiver, signals_filter, response)
                except Exception:
                    self.logger.exception(
                        '%s.send_robust exception thrown by receiver',
                        self.name)
                    continue
                else:
                    if response:
                        return (receiver, response)
        return False

    def _live_receivers(self):
        for receiver, signals_filter in self.receivers:
            if isinstance(receiver, WEAKREF_TYPES):
                receiver = receiver()
                if receiver is None:
                    continue
            yield (receiver, signals_filter)

    def _remove_receiver(self, receiver):
        """
        Called by saferef.safeRef on receiver deletion.
        """
        with self.lock:
            for index, (r, _) in enumerate(self.receivers):
                if r == receiver:
                    del self.receivers[index]
                    break
