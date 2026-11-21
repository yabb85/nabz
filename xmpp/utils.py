from threading import Thread
from asyncio.selector_events import _SelectorTransport


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ThreadReturn(Thread):
    """
    Create a new class to launch thread an retrieve return after execution
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super().__init__(group, target, name, args, kwargs)

    def run(self):
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return


class TransportOverride:
    """
    Overried original Transport class to send str instead if only bytes
    """
    def __init__(self, transport: _SelectorTransport):
        self._transport = transport

    def __getattr__(self, name):
        return getattr(self._transport, name)

    def write_str(self, message):
        print('Send:', message)
        self._transport.write(message.encode('utf-8'))
