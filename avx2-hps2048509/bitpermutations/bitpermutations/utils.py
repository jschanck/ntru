from functools import wraps


def split_in_size_n(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def reg_to_memfunc(f, in_size, out_size, per_reg=256):
    """ Makes a function that operates on registers use memory instead. """

    # To prevent circular imports
    from .instructions import vmovdqu
    from .data import Register

    @wraps(f)
    def memfunc(out_data, in_data):
        src = [Register(per_reg) for _ in range(in_size)]
        dst = [Register(per_reg) for _ in range(out_size)]

        for reg, mem in zip(src, in_data):
            vmovdqu(reg, mem)
        f(dst, src)
        for mem, reg in zip(out_data, dst):
            vmovdqu(mem, reg)
    return memfunc


def format_value(value, n=32):
    result = ""
    x = list(reversed(value))
    offset = 256 - len(x) % 256
    for i, a in enumerate(x):
        i += offset
        result += '{:^4}'.format(a)
        if i % 8 == 7:
            result += '|'
        if i % n == n-1:
            result += '\n'
    return result


def sequence_to_values(dst, seq, padding=None):
    seq = list(seq)
    for i, reg in enumerate(dst):
        if len(seq) >= reg.size:
            reg.value, seq = seq[:reg.size], seq[reg.size:]
        else:
            reg.value = seq + [padding] * (reg.size - len(seq))
            break
    else:
        if len(seq) > 0:
            raise Exception("Sequence did not fit in registers; "
                            "{} elements remaining".format(len(seq)))
