from .utils import TransportOverride
from random import SystemRandom
from base64 import b64encode


class AuthParser:
    def __init__(self, name, attrs, transport: TransportOverride):
        self._stack = {name: attrs}
        self._name = name
        self._nonce = 0
        self._transport = transport

    def remove_level(self, element: str):
        self._nonce = SystemRandom().randint(100,100000000000)
        challenge = f'nonce="{self._nonce}",qop="auth",charset=utf-8,algorithm=md5-sess'
        print(challenge)
        answer = f"<challenge xmlns='urn:ietf:params:xml:ns:xmpp-sasl'>{b64encode(challenge.encode()).decode()}</challenge>"
        self._transport.write_str(answer)
        del self._stack[element]

    def get_nonce(self):
        return self._nonce
