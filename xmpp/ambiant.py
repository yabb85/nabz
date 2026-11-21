from random import randint

class Ambiant:
    def __init__(self):
        self.tag = ''
        self._value = 0
        self._min = 0
        self._max= 255

    def set(self, value):
        if value < self._min and value > self._max:
            raise Exception
        self._value = value

    def get(self):
        return self._value

    def to_str(self):
        return f'{self._value:02x}'

    def __str__(self):
        return f'{self.tag}{self._value:02x}'

    def random(self):
        self._value = randint(self._min, self._max)


class Disable(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '00'
        self._value = 0
        self._max = 1


class Meteo(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '01'
        self._value = 0
        self._max = 5


class Bourse(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '02'
        self._value = 0
        self._max = 6

class Trafic(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '03'
        self._value = 0
        self._max = 6


class Ear(Ambiant):
    def __init__(self, value=0, right=True):
        super().__init__()
        if not right:
            self.tag = '04'
        else:
            self.tag = '05'
        self._value = value
        self._max = 16


class Mail(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '06'
        self._value = 0
        self._max = 3


class Air(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '07'
        self._value = 0

    def set(self, value):
        if value in [0, 5, 8]:
            self._value = value
        else:
            raise Exception


class Nose(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '08'
        self._value = 0
        self._max = 2


class BottomLED(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '09'
        self._value = 0
        self._max = 7


class Sleep(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '0b'
        self._value = 0
        self._max = 1

    def wake_up(self):
        self._value = False

    def sleep(self):
        self._value = True

    def set_bool(self, val):
        if val:
            self._value = 1
        else:
            self._value = 0


class Taichi(Ambiant):
    def __init__(self):
        super().__init__()
        self.tag = '0e'
        self._value = 0
