from base64 import b64decode, b64encode
from .bunny import BunnyManager
from re import compile as re_compile
from .utils import TransportOverride
AUTH_PATTERN = r'username="(?P<username>.*)",nonce="(?P<nonce>.*)",cnonce="(?P<cnonce>.*)",nc=(?P<nc>.*),qop=(?P<qop>.*),digest-uri="(?P<digest_uri>.*)",response=(?P<response>.*),charset=utf-8'
AUTH_REG = re_compile(AUTH_PATTERN)


class ResponseParser:
    def __init__(self, name, attrs, transport: TransportOverride, bunny):
        self._stack = {name: attrs}
        self._name = name
        self._transport = transport
        self._data = ''
        self._bunny = bunny

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        if self._name == element:
            self._transport.write_str(self._data)
        del self._stack[element]

    def process(self, content: str):
        byte_content = content.encode()
        data = b64decode(byte_content + b'=' * (-len(content) % 4))
        print(data)
        print(data.decode())
        plop = AUTH_REG.match(data.decode())
        print(plop)
        if plop:
            data = plop.groupdict()
            answer = ''
            if  self._bunny.authentication(data['username'], int(data['nonce']), data['cnonce'], data['nc'], data['digest_uri'], 'AUTHENTICATE', data['response']):
                rsp_auth = 'rspauth=' + self._bunny.compute_digest(data['username'], int(data['nonce']), data['cnonce'], data['nc'], data['digest_uri'], '')
                self._data = f"<challenge xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>{b64encode(rsp_auth.encode()).decode()}</challenge>"
                man = BunnyManager()
                man.add_bunny(self._bunny)
                self._data += "<success xmlns='urn:ietf:params:xml:ns:xmpp-sasl'/>"
            else:
                self._data = "<failure xmlns='urn:ietf:params:xml:ns:xmpp-sasl'><not-authorized/></failure>"
