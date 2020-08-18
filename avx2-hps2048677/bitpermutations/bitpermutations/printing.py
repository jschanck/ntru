from .data import MemoryFragment, ZERO
import bitpermutations.instructions as instructions
import bitpermutations.data as data
import bitpermutations.utils as utils
from .utils import reg_to_memfunc


def print_memfunc(f, in_size, out_size, per_reg=256, initialize=False):
    """Wraps a function that operates on registers in .data and .text sections,
    and makes it operate on memory fragments instead."""

    in_data = [MemoryFragment(per_reg, '{}(%rsi)'.format(per_reg*i // 8))
               for i in range(in_size)]
    out_data = [MemoryFragment(per_reg, '{}(%rdi)'.format(per_reg*i // 8))
                for i in range(in_size)]
    if initialize:
        utils.sequence_to_values(in_data, range(0, 677), padding=ZERO)

    instructions.reset()
    data.reset()

    f(out_data, in_data)

    print(".data")
    print(".section .rodata")
    print(".p2align 5")
    for mask in data.DATASECTION:
        print(mask.data())

    print(".text")
    print(".global {}".format(f.__name__))
    print(".global _{}".format(f.__name__))

    print("{}:".format(f.__name__))
    print("_{}:".format(f.__name__))
    for ins in instructions.INSTRUCTIONS:
        print(ins)

    print("ret")


def print_reg_to_memfunc(f, in_size, out_size, per_reg=256):
    f = reg_to_memfunc(f, in_size, out_size, per_reg)
    print_memfunc(f, in_size, out_size, per_reg)
