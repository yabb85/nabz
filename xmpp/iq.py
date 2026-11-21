from time import sleep
from .bunny import Bunny
from .utils import TransportOverride


class IQParser:
    def __init__(self, name, attrs, transport: TransportOverride, bunny: Bunny):
        self._stack = {name: attrs}
        self._name = name
        self._from = attrs.get('from')
        self._to = attrs.get('to')
        self._id = attrs.get('id')
        self._type = ''
        self._data = ''
        self._wake_up = False
        self._transport = transport
        self._bunny = bunny

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        if element == 'resource':
            if 'bind' in self._stack:
                self._bunny._resource = self._data
                print(f'bunny presence: {self._bunny._resource}')
            self._data = f'<jid>{self._from.split("/")[0]}/{self._data}</jid>'
        elif element == 'bind':
            bind = f"<bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'>{self._data}</bind>"
            self._data = bind
            self._type = 'result'
        elif element == 'unbind':
            self._data = ''
            self._type = 'result'
        elif element == 'session':
            self._type = 'result'
            self._data = "<session xmlns='urn:ietf:params:xml:ns:xmpp-session'/>"
        elif element == 'packet':
            self._data = f"<query xmlns='violet:iq:sources'>{self._data}</query>"
            self._type = 'result'
            self._wake_up = True
        elif  element == 'query' and self._stack[element].get('xmlns') == 'violet:iq:register':
            if self._data:
                self._data = ''
            else:
                self._data = "<query xmlns='violet:iq:register'><instructions>Choose a username and password to register with this server</instructions><username/><password/></query>"
            self._type = 'result'
        elif element == 'username':
            self._bunny._username = self._data
            self._data = ''
        elif element == 'password':
            self._bunny._password = self._data
            self._bunny.set_password(self._data)
            self._data = ''
            # self._type = 'set'
        elif element == self._name:
            packet = IQ(self._from, self._to, self._id, self._type, self._data).generate_packet()
            self._transport.write_str(packet)
            if self._wake_up:
                sleep(3)
                # self._bunny.wake_up()
                self._bunny.send_sleep()
                self._wake_up = False
                self._bunny.send_ears()
        else:
            self.process('')
        del self._stack[element]

    def process(self, content: str):
        self._data = content


class IQ:
    def __init__(self, attr_to, attr_from, attr_id, attr_type,  data):
        self._to = attr_to
        self._from = attr_from
        self._id = attr_id
        self._type = attr_type
        self._data = data

    def generate_packet(self) -> str:
        packet = '<iq'
        if self._to:
            packet += f" from='{self._from}'"
        if self._from:
            packet += f" to='{self._to}'"
        packet += f" id='{self._id}' type='{self._type}'"
        if self._data:
            packet += f">{self._data}</iq>"
        else:
            packet += "/>"
        return packet
