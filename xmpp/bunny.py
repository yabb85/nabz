from base64 import b64encode, b64decode
from hashlib import md5
import django
import os
from .utils import Singleton, ThreadReturn
from .ambiant import Meteo, Bourse, Trafic, Ear, Mail, Air, Nose, Sleep, Taichi, BottomLED, Disable
from .message import MessageSleep, MessageAmbiant, MessageBlock

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lapinou.settings')
django.setup()

from vl.models import Bunny as BunnyDB  # noqa: E402


def request_db(username):
    bunny = BunnyDB.objects.get(sn=username)
    return bunny


def set_password(username, password):
    # bunny = request_db(username)
    bunny = BunnyDB.objects.get(sn=username)
    bunny.password = password
    bunny.save()
    return bunny


def set_sleep_state(username, sleep_state):
    bunny = request_db(username)
    bunny.sleep_state = sleep_state
    bunny.save()


def set_connected_state(username, connected_state):
    bunny = request_db(username)
    bunny.connected = connected_state
    bunny.save()


class Bunny:

    def __init__(self, transport):
        self._username = None
        self._nonce = None
        self._response = None
        self._password = '4617d61cc796'
        self._authentified = False
        self._disable = Disable()
        self._meteo = Meteo()
        self._bourse = Bourse()
        self._trafic = Trafic()
        self._left_ear = Ear(right=False)
        self._right_ear = Ear()
        self._mail = Mail()
        self._air = Air()
        self._nose = Nose()
        self._bottom = BottomLED()
        self._sleep = Sleep()
        self._taichi = Taichi()
        self._transport = transport
        self._resource = None
        self._msg_nb = 0
        self._one_click = ''
        self._double_click = ''

    def authentication(self, username, nonce, cnonce, nc, digest_uri, mode, response):
        """
        check authentication permission
        """
        self._username = username
        t = ThreadReturn(target=request_db, args=[username])
        t.start()
        profile = t.join()
        self._password = profile.password
        self._sleep.set_bool(profile.sleep_state)
        self._authentified = response == self.compute_digest(username, nonce, cnonce, nc, digest_uri, mode)
        t = ThreadReturn(target=set_connected_state, args=[self._username, True])
        t.start()
        t.join()
        return self._authentified

    def disconnect(self):
        t = ThreadReturn(target=set_connected_state, args=[self._username, False])
        t.start()
        t.join()

    def compute_digest(self, username, nonce, cnonce, nc, digest_uri, mode):
        """
        Compute digest access authentication response (RFC 2617)
        """
        a1 = md5(f'{username}::{self._password}'.encode())
        ha1 = md5(a1.digest() + f':{nonce}:{cnonce}'.encode())
        ha2 = md5(f'{mode}:{digest_uri}'.encode())
        c_reponse = md5(f'{ha1.hexdigest()}:{nonce}:{nc}:{cnonce}:auth:{ha2.hexdigest()}'.encode())
        return c_reponse.hexdigest()

    def set_nonce(self, nonce):
        self._nonce = nonce

    def is_authentified(self):
        return self._authentified

    def set_password(self, value):
        """
        Set the password in database
        The password stored must be modified to match with password used by nabaztag in digest algorithm.
        password = hex(user ^ password)
        """
        plip = b''
        t1 = bytes.fromhex(self.get_username())
        t2 = bytes.fromhex(value)
        for a, b in zip(t1, t2):
            val = a ^ b
            plip += val.to_bytes()
        self._password = plip.hex()
        t = ThreadReturn(target=set_password, args=[self.get_username(), self._password])
        t.start()
        profile = t.join()
        print(profile)

    def tob64(self, value):
        return b64encode(bytes.fromhex(value))

    def fromb64(self, value):
        return b64decode(value).hex()

    def get_username(self):
        return self._username

    def send(self, packet):
        answer = f"<message from='net.lapinou.platform@{self._transport._transport._sock.getsockname()[0]}/services' to='{self._username}@{self._transport._transport._sock.getpeername()[0]}/{self._resource}' id='{self._msg_nb}'>{packet}</message>"
        self._msg_nb += 1
        self._transport.write_str(answer)

    def send_ambiant(self, ambiant_list):
        packet = MessageAmbiant(ambiant_list).generate_packet()
        self.send(packet)

    def send_ears(self):
        packet = MessageAmbiant([self._left_ear, self._right_ear]).generate_packet()
        self.send(packet)

    def send_nose(self):
        packet = MessageAmbiant([self._nose]).generate_packet()
        self.send(packet)

    def send_sleep(self):
        packet = MessageSleep(self._sleep).generate_packet()
        self.send(packet)
        t = ThreadReturn(target=set_sleep_state, args=[self._username, self._sleep.get()])
        t.start()
        profile = t.join()
        print(profile)

    def stop_ambiant(self):
        self._disable.set(1)
        packet = MessageAmbiant(self._disable).generate_packet()
        self.send(packet)

    def send_weather(self):
        packet = MessageAmbiant(self._meteo).generate_packet()
        self.send(packet)

    def send_trafic(self):
        packet = MessageAmbiant(self._trafic).generate_packet()
        self.send(packet)

    def send_stream(self, url):
        packet = MessageBlock('ST', url).generate_packet()
        self.send(packet)

    def send_block(self, data):
        packet = MessageBlock(None, data).generate_packet()
        self.send(packet)

    def one_click(self):
        self.send_block(f'CU http://tofu/vl/oneclick?sn={self._username}\nMW\n')

    def double_click(self):
        self.send_block(f'CU http://tofu/vl/doubleclick?sn={self._username}\nMW\n')

    def ears_move(self):
        print('ears move')
        self.send_block(f'CU http://tofu/vl/earsmove?sn={self._username}&left={self._left_ear.get()}&right={self._right_ear.get()}\n')

    def rfid(self):
        print('rfid')

    def cron(self):
        print('cron')

    def wake_up(self):
        self._sleep.wake_up()

    def sleep(self):
        self._sleep.sleep()

    def set_ears(self, side: str, value: int):
        if side == 'right':
            self._right_ear.set(value)
        elif side == 'left':
            self._left_ear.set(value)
        else:
            raise Exception

    def set_weather(self, val):
        self._meteo.set(val)


class BunnyManager(metaclass=Singleton):
    _bunny = {}

    def add_bunny(self, bunny: Bunny):
        self._bunny[bunny.get_username()] = bunny

    def remove_bunny(self, username):
        self._bunny.pop(username)

    def get_bunny(self, bunny_name) -> Bunny:
        return self._bunny.get(bunny_name, None)
