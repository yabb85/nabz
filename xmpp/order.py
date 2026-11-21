from .utils import TransportOverride
from .bunny import BunnyManager

class OrderParser:
    def __init__(self, name, attrs, transport: TransportOverride):
        self._stack = {name: attrs}
        self._name = name
        self._sn = attrs.get('sn')
        self._transport = transport
        self._bunny = BunnyManager().get_bunny(self._sn)
        self._content = []

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        del self._stack[element]
        if self._bunny:
            if element == 'block':
                print(f'remove_level content: {self._content}')
                data = ''
                for content in self._content:
                    data += content
                self._bunny.send_block(data)
            elif element == 'sleep':
                if self._content[0] == 'sleep':
                    self._bunny.sleep()
                else:
                    self._bunny.wake_up()
                self._bunny.send_sleep()
            elif element == 'ears':
                self._bunny.send_ears()
            elif element == 'right':
                self._bunny.set_ears(element, int(self._content[0]))
            elif element == 'left':
                self._bunny.set_ears(element, int(self._content[0]))
            elif element == 'weather':
                self._bunny.set_weather(int(self._content[0]))
                self._bunny.send_weather()
            elif element == 'nose':
                self._bunny._nose.set(int(self._content[0]))
                self._bunny.send_nose()
            elif element == 'mail':
                self._bunny._mail.set(int(self._content[0]))
                self._bunny.send_ambiant([self._bunny._mail])
            elif element == 'disable':
                self._bunny.stop_ambiant()
            elif element == 'ambiant':
                pass  # TODO: trouver un moyen d'envoyer tout ce qui est ambiant d'un coup
        self._content.clear()

    def process(self, content: str):
        print(f'content: {content}')
        self._content.append(content)
