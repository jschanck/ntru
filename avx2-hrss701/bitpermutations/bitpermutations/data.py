from .utils import split_in_size_n
import gc
import random

UNKNOWN = '?'
ZERO = '-'
ONE = '#'

tokens = [UNKNOWN, ZERO, ONE]

DATASECTION = []
SALT = ''  # prevents duplicate labels


def reset():
    global DATASECTION, SALT
    DATASECTION = []
    SALT = '{:16x}'.format(random.randint(0, 2**128))


class AllocationError(Exception):

    def __init__(self, message):
        self.message = message


class DataFragment():

    def __init__(self, size):
        self.size = size
        self._value = [UNKNOWN] * size

    def __iter__(self):
        yield from self._value

    def __len__(self):
        return self.size

    def __getitem__(self, i):
        return self._value[i]

    def bitstring(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        # TODO validation goes here
        if len(val) != self.size:
            raise Exception("Setting {} bits, but is of size {}"
                            .format(len(val), self.size))
        for x in val:
            if type(x) is not int and x not in tokens:
                raise Exception("Value contained unrecognized {}".format(x))
        self._value = [x for x in val]


class Register(DataFragment):

    available = {
        256: list(reversed(range(16))),
        # TODO consider callee-saved registers as well
        64: ['rax', 'rcx', 'rdx', 'r8', 'r9', 'r10', 'r11'],
    }

    callee_saveable = {
        64: ['rbp', 'rbx', 'r12', 'r13', 'r14', 'r15'],
    }

    callee_saved = {
        64: [],
    }

    def __init__(self, size=256, allocate=True):
        DataFragment.__init__(self, size)
        try:
            if allocate:
                self.number = self.available[size].pop()
        except IndexError:
            gc.collect()
            try:
                self.number = self.available[size].pop()
            except IndexError:
                raise AllocationError("Cannot allocate >16 registers.")

    def free(self):
        if hasattr(self, 'number') and self.number is not None:
            try:
                self.ymm
            except AttributeError:
                self.available[self.size].append(self.number)
                self.number = None

    def __del__(self):
        self.free()

    @staticmethod
    def regnumber_to_str(number, size):
        if size == 256:
            return '%ymm{}'.format(number)
        elif size == 128:
            return '%xmm{}'.format(number)
        elif size == 64:
            return '%{}'.format(number)
        else:
            raise NotImplementedError("Unrecognized register size")

    def __str__(self):
        if not hasattr(self, 'number'):
            return "Unallocated register"
        return self.regnumber_to_str(self.number, self.size)

    @classmethod
    def xmm_from_ymm(cls, ymm):
        xmm = cls(128, allocate=False)
        xmm.number = ymm.number
        xmm.ymm = ymm
        xmm.value = ymm.value[:128]
        return xmm

    @classmethod
    def push_callee_saved(cls, size):
        try:
            reg_name = cls.callee_saveable[size].pop()
            cls.available[size].append(reg_name)
            cls.callee_saved[size].append(reg_name)
        except IndexError:
            raise AllocationError("No more registers available to save.")
        return Register.regnumber_to_str(reg_name, size)

    @classmethod
    def pop_callee_saved(cls, size):
        try:
            reg_name = cls.callee_saved[size].pop()
        except IndexError:
            raise AllocationError("Already restored callee-saved registers.")
        try:
            cls.available[size].remove(reg_name)
        except ValueError:
            raise AllocationError("Trying to restore callee-saved registers, "
                                  "but not all have been freed.")
        return Register.regnumber_to_str(reg_name, size)


class MemoryFragment(DataFragment):

    def __init__(self, size, label, value=None):
        """ Note: a label can also be an offset register (e.g. 32(%rsi)). """
        super().__init__(size)
        if value:
            self._value = value
        else:
            self._value = [UNKNOWN] * size
        self.size = size
        self.label = label

    def __str__(self):
        return self.label


class Mask(DataFragment):

    maskindex = 0

    def __init__(self, value, size=256):
        super().__init__(size)
        if size % len(value) != 0:
            raise Exception("Length of mask must divide its size")
        wsize = size // len(value)
        if type(value) is str:
            if any(x not in '01' for x in value):
                raise ValueError("Mask must consist of 0s and 1s")
            self.value = sum(([(ONE if x == '1' else ZERO)] * wsize
                              for x in reversed(value)), [])
        elif type(value) is list:
            if any(x not in [ONE, ZERO] for x in value):
                raise ValueError("Mask must consist of ONEs and ZEROs")
            self.value = sum(([x] * wsize for x in value), [])
        else:
            raise TypeError("Mask must be either string or list of bits")
        self.maskindex = Mask.maskindex
        Mask.maskindex += 1
        DATASECTION.append(self)

    def __str__(self):
        return "mask_{}_{}".format(self.maskindex, SALT)

    def data(self):
        output = "{}:\n".format(str(self))
        if self.size % 16 != 0:
            raise NotImplementedError("Can only divide masks into words")
        # TODO this can be optimized by dividing into order sizes
        words = split_in_size_n(self.value, 16)
        for word in words:
            word = reversed(['1' if x is ONE else '0' for x in word])
            word = int(''.join(word), 2)
            output += ".word {}\n".format(hex(word))
        return output

    @classmethod
    def as_immediate(cls, value):
        out = 0
        for v in reversed(value):
            out = out << 1 | int(v is ONE)
        return out

    @classmethod
    def from_immediate(cls, value, size=64):
        result = []
        while len(result) < size:
            result.append(ONE if value & 1 else ZERO)
            value >>= 1
        return result

    @classmethod
    def degree(cls, value):
        for i, x in reversed(list(enumerate(value))):
            if x == ONE:
                return i

    @classmethod
    def consec(cls, value, from_zero=False):
        if from_zero:
            value = ''.join(value).rstrip(ZERO)
        else:
            value = ''.join(value).strip(ZERO)
        return all(x == ONE for x in value)


class MaskRegister(Register, Mask):
    """ This class allows for validation when masks are moved to registers"""
    pass


class IndicesMask(Mask):

    def __init__(self, indices, size=256):
        if len(indices) is not size // 8:
            raise NotImplementedError("IndicesMask only supports byte indices")
        if any(type(x) is not int and x is not None for x in indices):
            raise TypeError("IndicesMask must contain indices or None-value")
        if any(x is not None and not 0 <= int(x) < size // 8 for x in indices):
            raise ValueError("Indices must be between 0 and number of bytes")
        self.size = size
        self.indices = indices
        self.maskindex = Mask.maskindex
        Mask.maskindex += 1
        DATASECTION.append(self)

    def __getitem__(self, i):
        return self.indices[i]

    def __iter__(self):
        yield from self.indices

    def __len__(self):
        return self.size // 8

    def data(self):
        output = "{}:\n".format(str(self))
        # TODO we still assume bytewise indices
        for i in self.indices:
            if i is None:
                i = 255
            output += ".byte {}\n".format(i)
        return output
