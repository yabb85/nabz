from .utils import TransportOverride


class PresenceParser:
    def __init__(self, name, attrs, transport: TransportOverride):
        self._stack = {name: attrs}
        self._name = name
        self._from = attrs.get('from')
        self._id = attrs.get('id')
        self._transport = transport

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        del self._stack[element]
        self._transport.write_str(f"<presence from='{self._from}' id='{self._id}'></presence>")

    def process(self, content: str):
        pass
