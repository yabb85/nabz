import asyncio
import socket
import sys
import warnings
from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from .bunny import Bunny
from .iq import IQParser
from .stream import StreamParser
from .auth import AuthParser
from .utils import TransportOverride
from .response import ResponseParser
from .message import MessageParser
from .presence import PresenceParser
from .order import OrderParser



class StreamAlivenessMonitor:
    """
    This class is a helper to monitor the aliveness of a stream. It will call a callback if the stream is not alive after a timeout.
    """

    def __init__(self, timeout=60, callback=None):
        self._timeout = timeout
        self._timeout_callback = callback
        self._timeout_task = None
        self._reset_event = asyncio.Event()

    def __del__(self):
        self.cancel()

    async def _timeout_task_coro(self):
        try:
            await asyncio.wait_for(self._reset_event.wait(), timeout=self._timeout)
        except asyncio.TimeoutError:
            if self._timeout_callback is not None:
                self._timeout_callback()

    def reset(self):
        """
            Reset the timer. Called always after received a message from the client/server
        """
        if self._timeout_task is not None:
            self._reset_event.set()
            self._timeout_task.cancel()
        self._reset_event.clear()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._timeout_task = asyncio.create_task(self._timeout_task_coro())

    def cancel(self):
        if self._timeout_task is not None:
            self._timeout_task.cancel()


class XMLHandler(ContentHandler):
    def __init__(self, transport, bunny):
        super().__init__()
        self._transport = transport
        self._bunny = bunny
        self._stack = []
        self._state = None
        self._element = None
        print(f'init handler {self._transport}')

    def startDocument(self):
        print('startDocument')

    def startElement(self, name, attrs):
        # print(f'startElement: {name}')
        if self._element:
            self._element.add_level(name, attrs)
        elif name == 'stream:stream':
            connected = self._bunny and self._bunny.is_authentified()
            self._element = StreamParser(name, attrs, self._transport, connected)
            del self._element
            self._element = None
        elif name == 'iq':
            self._element = IQParser(name, attrs, self._transport, self._bunny)
        elif name == 'auth':
            self._element = AuthParser(name, attrs, self._transport)
        elif name == 'response':
            self._element = ResponseParser(name, attrs, self._transport, self._bunny)
        elif name == 'presence':
            self._element = PresenceParser(name, attrs, self._transport)
        elif name == 'message':
            self._element = MessageParser(name, attrs, self._transport, self._bunny)
        elif name == 'order':
            self._element = OrderParser(name, attrs, self._transport)

    def endElement(self, name):
        # print(f'endElement: {name}')
        self._element.remove_level(name)
        if name == 'auth':
            self._bunny.set_nonce(self._element.get_nonce())
        if name == self._element._name:
            self._element = None

    def endDocument(self):
        print('endDocument called only at the end of stream')

    def characters(self, content):
        # print(f'content -> {content}')
        self._element.process(content)


class XMLProtocol(asyncio.Protocol):
    def __init__(self):
        print('XMLProtocol')
        self._xmlns = 'jabber:client'
        self._connection_timeout = 60
        self._peer = None
        self._transport = None
        self._handler = None
        self._parser = None
        self._bunny = None
        self._timeout_monitor = None
        self._nb_stream = 0

    def connection_made(self, transport):
        print('connection_made')
        print(transport)
        if transport:
            self._peer = transport.get_extra_info('peername')
            self._transport = TransportOverride(transport)
            self._bunny = Bunny(self._transport)
            self._parser = make_parser()
            self._handler = XMLHandler(self._transport, self._bunny)
            self._parser.setContentHandler(self._handler)
            self._timeout_monitor = StreamAlivenessMonitor(timeout=60, callback=self.connection_timeout)

    def connection_lost(self, exc):
        print('connection_lost')
        print(exc)
        print(self._transport._transport._sock.getsockname())
        self._timeout_monitor.cancel()

    def data_received(self, data):
        print(f'data_received: {data}')
        self._timeout_monitor.reset()
        if data == b' ' and self._bunny._resource == 'streaming':
            print('yolo')
            # data = "<query xmlns='jabber:iq:version'/>"
            # packet = IQ(attr_to=f'{self._bunny._username}@{self._transport._transport._sock.getsockname()[0]}/{self._bunny._resource}', attr_from=f'net.lapinou.platform@{self._transport._transport._sock.getpeername()[0]}/{self._bunny._resource}', attr_id=self._nb_stream, attr_type='get', data=data).generate_packet()
            # self._transport.write_str(packet)
            # self._nb_stream += 1
        else:
            try:
                data = data.replace(b"<?xml version='1.0' encoding='UTF-8'?>", b"").decode().strip()
                self._parser.feed(data)
            except UnicodeDecodeError:
                pass

    def oef_received(self):
        print('oef_received')

    def connection_timeout(self):
        print('connection_timeout')
        self._bunny.disconnect()
        # BunnyManager().remove_bunny(self._bunny.get_username())


class Server:

    def __init__(self):
        print('Server')
        self._host = '192.168.1.21'
        self._port = 5222
        self._family = socket.AF_INET
        self._listener = None

    async def run_server(self):
        print('run_server')
        loop = asyncio.get_running_loop()
        self._listener = await loop.create_server(
            lambda: XMLProtocol(),
            host=self._host,
            port=self._port,
            family=self._family,
        )
        while True:
            await asyncio.sleep(3600)

    async def start(self):
        print('start')
        tasks = [
            asyncio.create_task(self.run_server())
        ]
        await asyncio.gather(*tasks)
        for task in tasks:
            _ = task.cancel()

        await asyncio.gather(*tasks)


def main():
    print('main')
    server = Server()
    asyncio.run(server.start(), debug=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
