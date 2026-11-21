from base64 import b64decode, b64encode
from .ambiant import Ambiant, Sleep
from .utils import TransportOverride


class MessageParser:
    def __init__(self, name, attrs, transport: TransportOverride, bunny):
        self._stack = {name: attrs}
        self._name = name
        self._from = attrs.get('from')
        self._to = attrs.get('to')
        self._id = attrs.get('id')
        self._transport = transport
        self._bunny = bunny
        self._data = ''

    def add_level(self, element: str, attrs):
        self._stack[element] = attrs

    def remove_level(self, element: str):
        if 'clic' == element:
            val = int(self._data)
            if val == 1:
                self._bunny.one_click()
            elif val == 2:
                self._bunny.double_click()
            else:
                print('error')
        elif 'left' == element or 'right' == element:
            print(f'ears {element} moved to {self._data}')
            self._bunny.set_ears(element, int(self._data))
            # self._bunny.set_ears(element, 10)
        elif 'ears' in self._stack.keys():
            print('ears closed')
            self._bunny.ears_move()
        del self._stack[element]

    def process(self, content: str):
        self._data = content


class Message:
    header = '7f'
    footer = 'ff'

    def __init__(self):
        self._trame = ''

    def tob64(self, value):
        return b64encode(bytes.fromhex(value))

    def fromb64(self, value):
        return b64decode(value).hex()

    def _generate_status(self):
        self._trame = ''

    def generate_packet(self):
        self._generate_status()
        status = self.tob64(self._trame).decode()
        packet = f"<packet xmlns='violet:packet' format='1.0' ttl='604800'>{status}</packet>"
        return packet


class MessageAmbiant(Message):
    def __init__(self, ambiant: list[Ambiant]|Ambiant):
        super().__init__()
        if type(ambiant) is not list:
            tmp = [ambiant]
        else:
            tmp = ambiant
        self._ambiant: list[Ambiant] = tmp

    def _generate_status(self):
        block = '04'
        data = '7ffffffe'
        for ambiant in self._ambiant:
            data += str(ambiant)
            print(ambiant)
            print(data)
        size = int(len(data) / 2)
        print(size)
        print(len(data))
        print(data)
        self._trame = f'{self.header}{block}{size:06x}{data}{self.footer}'
        print(self._trame)


class MessageBlock(Message):
    def __init__(self, block_type: str, data: str):
        """
        MU ou MC lire un fichier de mp3 a l'url indiqué limité a des mp3 de petites taille ~20s
        MI lire un fichier de midi a l'url indiqué ???
        MW attend que la lecture de son soit finie
        TA start taichi ???
        RB reboot ???
        ST commence le streaming
        SP streaming en mode protect
        CH execute un choregraphie
        CU appel une url
        CL ???
        PL ???
        """
        super().__init__()
        self.block_type = block_type
        # self.data = data + '\nPL 3\nMW\n'
        self.data = data
        self.inversion_table = [1, 171, 205, 183, 57, 163, 197, 239, 241, 27, 61, 167, 41, 19, 53, 223, 225, 139, 173, 151, 25, 131, 165, 207, 209, 251, 29, 135, 9, 243, 21, 191, 193, 107, 141, 119, 249, 99, 133, 175, 177, 219, 253, 103, 233, 211, 245, 159, 161, 75, 109, 87, 217, 67, 101, 143, 145, 187, 221, 71, 201, 179, 213, 127, 129, 43, 77, 55, 185, 35, 69, 111, 113, 155, 189, 39, 169, 147, 181, 95, 97,11, 45, 23, 153, 3, 37, 79, 81, 123, 157, 7, 137, 115, 149, 63, 65, 235, 13, 247, 121, 227, 5, 47, 49, 91, 125, 231, 105, 83, 117, 31, 33, 203, 237, 215, 89, 195, 229, 15, 17, 59, 93, 199, 73, 51, 85, 255]

    def _generate_status(self):
        block = '0a'
        if self.block_type == 'MW':
            pass
        elif not self.block_type:
            encoded = self.encode(f'{self.data}')
            print(encoded)
            size = int(len(encoded) / 2)
            self._trame = f'{self.header}{block}{size:06x}{encoded}{self.footer}'
            print(self._trame)
        else:
            encoded = self.encode(f'{self.block_type} {self.data}')
            size = int(len(encoded) / 2)
            self._trame = f'{self.header}{block}{size:06x}{encoded}{self.footer}'

    def decode(self, data) -> str:
        """
        convert hex trame to readable string
        """
        data_hex = bytes.fromhex(data)
        res = []
        previous = 35
        for i in range(1, len(data_hex)):
            a = data_hex[i] - 47
            b = 1 + 2 * previous
            previous = (a * b) % 256
            res.append(previous)
        return bytes(res).decode()

    def encode(self, data) -> str:
        """
        convert readable string to hex trame
        """
        data_bytes = data.encode()
        print(data_bytes)
        res = [0]
        previous = 35
        for i in range(0, len(data_bytes)):
            current = data_bytes[i]
            plop = (self.inversion_table[previous % 128] * current + 47) % 256
            previous = current
            res.append(plop)
        return bytes(res).hex()



class MessageSleep(Message):
    def __init__(self, sleep: Sleep):
        super().__init__()
        self._sleep = sleep

    def _generate_status(self):
        block = '0b'
        self._trame = f'{self.header}{block}000001{self._sleep.to_str()}{self.footer}'


class MessageReboot(Message):
    def __init__(self):
        super().__init__()

    def _generate_status(self):
        block = '09'
        self._trame = f'{self.header}{block}{self.footer}'


class MessageClean(Message):
    def __init__(self):
        super().__init__()

    def _generate_status(self):
        self._trame = ''
