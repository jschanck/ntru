from bitpermutations.data import (ONE, ZERO,
                                  Register, Mask, IndicesMask, MaskRegister,
                                  AllocationError)
import bitpermutations.instructions as x86
from bitpermutations.printing import print_memfunc
from bitpermutations.utils import reg_to_memfunc, split_in_size_n
import argparse
import functools
from collections import OrderedDict


def gen_sequence(e, N):
    def interleave(seq):
        if len(seq) % 2 == 0:
            return [x for t in zip(seq[:len(seq) // 2],
                                   seq[len(seq) // 2:]) for x in t]
        else:
            return ([x for t in zip(seq[:len(seq) // 2],
                                    seq[len(seq) // 2 + 1:]) for x in t] +
                    [seq[len(seq) // 2]])
    seq = list(range(N))
    for i in range(e):
        seq = interleave(seq)
    return seq


def registers_to_sequence(registers):
    result = sum((x.value for x in registers), [])
    while result[-1] is ZERO:
        result.pop()
        if not result:
            break
    return result


def square_509_patience(out_data, in_data, n, callee_saved=0):
    x = list(range(509)) + 3*[ZERO]
    regs = split_in_size_n(x, 64)

    seq = gen_sequence(n, 509) + 3*[ZERO]
    seq_r = split_in_size_n(seq, 64)

    moved = [False] * len(seq_r)

    r = Register(64)
    t1 = Register(64)

    for i in range(callee_saved):
        x86.push_callee_saved(64)

    maskcache = OrderedDict()

    def mask_to_register(mask):
        mask = Mask.as_immediate(mask)
        if mask in maskcache:
            maskcache.move_to_end(mask)
            return maskcache[mask]
        try:
            maskreg = MaskRegister(64, mask)
        except AllocationError:
            _, maskreg = maskcache.popitem(False)
        x86.mov(maskreg, mask)
        maskcache[mask] = maskreg
        return maskreg

    for j, inreg in enumerate(regs):
        x86.mov(r, in_data[j])
        for i, seqreg in enumerate(seq_r):
            piledict = {}
            for rotation in range(64):
                ror_seqreg = seqreg[rotation:] + seqreg[:rotation]
                piles = []
                overlap = [x for x in ror_seqreg if x in inreg and x != ZERO]
                for x in overlap:
                    for pile in piles:
                        try:
                            if pile[-1] <= x:
                                pile.append(x)
                                break
                        except IndexError:  # pile is empty
                            pass
                    else:  # doesn't fit on any existing pile: start a new pile
                        piles.append([x])
                piledict[rotation] = piles
            min_pile_key = min(piledict, key=lambda x: len(piledict.get(x)))
            if len(piledict[0]) == len(piledict[min_pile_key]):
                min_pile_key = 0
            if min_pile_key > 0:
                ror_seqreg = seqreg[min_pile_key:] + seqreg[:min_pile_key]
            else:
                ror_seqreg = seqreg

            for pile in piledict[min_pile_key]:
                emask = [ZERO] * 64
                for bit in pile:
                    emask[inreg.index(bit)] = ONE
                dmask = [ZERO] * 64
                for bit in pile:
                    dmask[ror_seqreg.index(bit)] = ONE

                # For consecutive bits, we do not even need pext/pdep
                if (Mask.consec(dmask) and Mask.consec(emask) and
                        (Mask.degree(emask) < 32 or Mask.degree(dmask) < 32)):
                    delta = (Mask.degree(dmask) - Mask.degree(emask)) % 64
                    x86.mov(t1, r)
                    if Mask.degree(emask) < 32:
                        x86.iand(t1, Mask.as_immediate(emask))
                        x86.rol(t1, delta + min_pile_key)
                        min_pile_key = 0  # to avoid two rols
                    else:
                        x86.rol(t1, delta)
                        x86.iand(t1, Mask.as_immediate(dmask))
                else:
                    # if we can extract using AND instead..
                    if Mask.consec(emask, True) and Mask.degree(emask) < 32:
                        x86.mov(t1, r)
                        x86.iand(t1, Mask.as_immediate(emask))
                    else:
                        x86.pext(t1, r, mask_to_register(emask))
                    x86.pdep(t1, t1, mask_to_register(dmask))

                if min_pile_key > 0:
                    x86.rol(t1, min_pile_key)
                if moved[i]:  # stored per i, as it's not the outer loop
                    x86.xor(out_data[i], t1)
                else:
                    x86.mov(out_data[i], t1)
                    moved[i] = True

    for mask in maskcache.values():
        mask.free()

    for i in range(callee_saved):
        x86.pop_callee_saved(64)


def square_509_shufbytes(out_data, in_data, n):
    r = Register()
    out = [Register() for _ in range(2)]
    moved = [False] * 2

    t1 = Register()
    t2 = Register()
    t3 = Register()
    t4 = Register()
    t5 = Register()

    seq = gen_sequence(n, 509) + 3*[ZERO]
    seq_regvalues = split_in_size_n(seq, 256)

    for in_data_fragment in in_data:
        x86.vmovdqa(r, in_data_fragment)
        shift_in = shifted = r
        offset = 0
        for delta in range(8):  # 8 possible rotations may be necessary
            rol_meta = None
            if delta > 0:
                # if we've made the previous rotation persistent
                if shift_in is shifted:
                    shifted = t4 if shifted is t3 else t3
                d_nett = delta - offset
                rol_meta = len(x86.INSTRUCTIONS), str(shifted), str(t1)
                x86.macro_v256rol(shifted, shift_in, d_nett, t1, t2)
                rotated = [b for d in range(d_nett) for b in shifted[d::64]]
            # vpshufb cannot cross over xmm lanes
            for swap_xmms in [False, True]:
                if swap_xmms:
                    swapped = t5
                    x86.vpermq(swapped, shifted, '01001110')
                else:
                    swapped = shifted
                r_bytes = split_in_size_n(swapped, 8)
                while True:  # could be necessary to extract twice from same r
                    bitmask = [[] for _ in range(len(seq_regvalues))]
                    shufmask = [None] * 32
                    for k, seq_value in enumerate(seq_regvalues):
                        s_bytes = split_in_size_n(seq_value, 8)
                        s_xmms = split_in_size_n(s_bytes, 16)
                        r_xmms = split_in_size_n(r_bytes, 16)
                        for i, (s128, r128) in enumerate(zip(s_xmms, r_xmms)):
                            for l, s_byte in enumerate(s128):
                                for m, r_byte in enumerate(r128):
                                    # if this byte is already taken;
                                    if (shufmask[i*16 + l] is not None and
                                            shufmask[i*16 + l] != m):
                                        continue
                                    bits = [ONE if x == y and x != ZERO
                                            else ZERO
                                            for x, y in zip(r_byte, s_byte)]
                                    if ONE not in bits:
                                        continue
                                    shufmask[i*16 + l] = m
                                    bitmask[k] += bits
                                    break
                                else:
                                    bitmask[k] += [ZERO] * 8
                                    continue
                                for m, (x, y) in enumerate(zip(bits, s_byte)):
                                    if x == ONE:
                                        seq_regvalues[k][i*128+l*8 + m] = None
                                s_bytes = split_in_size_n(seq_regvalues[k], 8)
                    if all(x is None for x in shufmask):
                        break
                    x86.vpshufb(t2, swapped, IndicesMask(shufmask))
                    for k, seq_value in enumerate(seq_regvalues):
                        if ONE not in bitmask[k]:
                            continue
                        if not moved[k]:
                            x86.vpand(out[k], t2, Mask(bitmask[k]))
                            moved[k] = True
                        else:
                            x86.vpand(t1, t2, Mask(bitmask[k]))
                            x86.vpxor(out[k], out[k], t1)
                        # check if we used any of the rotated bits
                        for maskbit, bit in zip(bitmask[k], t2):
                            if delta > 0 and bit in rotated and maskbit is ONE:
                                rol_meta = None

            # TODO this is an ugly hack that should be abstracted
            if rol_meta is not None:
                i, dest, temp = rol_meta
                del x86.INSTRUCTIONS[i]  # delete srlq
                x86.INSTRUCTIONS[i] = x86.INSTRUCTIONS[i].replace(temp, dest)
                del x86.INSTRUCTIONS[i+1]  # delete permq
                del x86.INSTRUCTIONS[i+1]  # delete xor
            else:
                # if we're keeping the rotation, make it persistent so that the
                # next rotation is smaller (and thus more likely ignorable)
                shift_in = shifted
                offset = delta

    for m, r in zip(out_data, out):
        x86.vmovdqa(m, r)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Output squaring routines.')
    parser.add_argument('no_of_squarings', type=int,
                        help='the number of repeated squarings')
    parser.add_argument('--callee', type=int, dest='callee', default=0,
                        help='the number of callee-saved registers to save')
    parser.add_argument('--patience', dest='patience', action='store_true',
                        help='always use the patience-sort method')
    parser.add_argument('--shufbytes', dest='shufbytes', action='store_true',
                        help='always use the shufbytes method')
    parser.add_argument('--raw-name', dest='raw_name', action='store_true',
                        help='use minimal function name (square_N_509)')
    parser.set_defaults(patience=False)

    args = parser.parse_args()
    if args.shufbytes:
        f = functools.partial(square_509_shufbytes, n=args.no_of_squarings)
        if args.raw_name:
            f.__name__ = "square_{}_509".format(args.no_of_squarings)
        else:
            f.__name__ = "square_{}_509_shufbytes".format(args.no_of_squarings)
        print_memfunc(f, 2, 2, initialize=True)
    elif args.patience:
        f = functools.partial(square_509_patience,
                              n=args.no_of_squarings, callee_saved=args.callee)
        if args.raw_name:
            f.__name__ = "square_{}_509".format(args.no_of_squarings)
        else:
            f.__name__ = "square_{}_509_patience".format(args.no_of_squarings)
        print_memfunc(f, 8, 8, per_reg=64)
    else:
        raise NotImplementedError(
            "There is no dedicated implementation for {} squarings. "
            "Please specify either --shufbytes or --patience."
            .format(args.no_of_squarings)
        )
