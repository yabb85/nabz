from datetime import datetime
from .utils import TransportOverride


class StreamParser:
    def __init__(self, name, attrs, transport: TransportOverride, connected):
        self._stack = {name: attrs}
        self._to = attrs.get('to')
        self._name = name
        self._connected = connected
        self._first= True
        self._data = ''
        self._transport = transport
        packet = self.generate_packet()
        self._transport.write_str(packet)
        packet = self.generate_packet()
        self._transport.write_str(packet)

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        del self._stack[element]

    def process(self, content: str):
        pass

    def generate_packet(self) -> str:
        if self._first:
            self._first = False
            data = f"<?xml version='1.0'?><stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' id='{int(datetime.utcnow().timestamp())}' from='{self._to}' version='1.0' xml:lang='en'>"
        elif self._connected:
            data = "<stream:features><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><required/></bind><unbind xmlns='urn:ietf:params:xml:ns:xmpp-bind'/><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></stream:features>"
        else:
            data = "<stream:features><mechanisms xmlns='urn:ietf:params:xml:ns:xmpp-sasl'><mechanism>DIGEST-MD5</mechanism><mechanism>PLAIN</mechanism></mechanisms><register xmlns='http://violet.net/features/violet-register'/></stream:features>"
        return data
