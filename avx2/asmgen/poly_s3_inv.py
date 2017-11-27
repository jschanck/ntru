from math import ceil

p = print

# TODO we do not need to do a full reduction here, but right now that's easiest
def mod3(a, r=13, t=14, c=15):
    # r = (a >> 8) + (a & 0xff); // r mod 255 == a mod 255
    p("vpsrlw $8, %ymm{}, %ymm{}".format(a, r))
    p("vpand mask_ff, %ymm{}, %ymm{}".format(a, a))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 4) + (r & 0xf); // r' mod 15 == r mod 15
    p("vpand mask_f, %ymm{}, %ymm{}".format(r, a))
    p("vpsrlw $4, %ymm{}, %ymm{}".format(r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    for _ in range(2):
        p("vpand mask_3, %ymm{}, %ymm{}".format(r, a))
        p("vpsrlw $2, %ymm{}, %ymm{}".format(r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    #   t = r - 3;
    p("vpsubw mask_3, %ymm{}, %ymm{}".format(r, t))
    #   c = t >> 15;  t is signed, so shift arithmetic
    p("vpsraw $15, %ymm{}, %ymm{}".format(t, c))

    tmp = a
    #   return (c&r) ^ (~c&t);
    p("vpandn %ymm{}, %ymm{}, %ymm{}".format(t, c, tmp))
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(c, r, t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, tmp, r))


def mul_mod3(r, a, b, t=15, a_from_mem=False):
    # /* Multiplication and lazy reduction to two bits */
    # r[0] = (a[0] & b[0]) ^ (a[1] & b[1]);
    a_lookup = '{}(%rsp)' if a_from_mem else '%ymm{}'
    p(("vpand "+a_lookup+", %ymm{}, %ymm{}").format(a[0], b[0], r[0]))
    p(("vpand "+a_lookup+", %ymm{}, %ymm{}").format(a[1], b[1], t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(r[0], t, r[0]))
    # r[1] = (a[0] & b[1]) ^ (a[1] & b[0]);
    p(("vpand "+a_lookup+", %ymm{}, %ymm{}").format(a[0], b[1], r[1]))
    p(("vpand "+a_lookup+", %ymm{}, %ymm{}").format(a[1], b[0], t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(r[1], t, r[1]))
    # /* Full reduction */
    # t = r[0] & r[1];
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(r[0], r[1], t))
    # r[0] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, r[0], r[0]))
    # r[1] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, r[1], r[1]))


def poly_s3_fmadd(a, b, s, t0=13, t1=14, t2=15, b_from_mem=False):
    """ assumes a, b and s are pairs of a low and a high register """
    d = [t0, t1]
    t = t2

    # /* Multiplication and lazy reduction to two bits */
    # d[0] = (b[0] & s[0]) ^ (b[1] & s[1]);
    b_lookup = '{}(%rsp)' if b_from_mem else '%ymm{}'
    p(("vpand "+b_lookup+", %ymm{}, %ymm{}").format(b[0], s[0], d[0]))
    p(("vpand "+b_lookup+", %ymm{}, %ymm{}").format(b[1], s[1], t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(d[0], t, d[0]))
    # d[1] = (b[0] & s[1]) ^ (b[1] & s[0]);
    p(("vpand "+b_lookup+", %ymm{}, %ymm{}").format(b[1], s[0], d[1]))
    p(("vpand "+b_lookup+", %ymm{}, %ymm{}").format(b[0], s[1], t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(d[1], t, d[1]))
    # /* Full reduction */
    # t = d[0] & d[1];
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(d[0], d[1], t))
    # d[0] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, d[0], d[0]))
    # d[1] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, d[1], d[1]))

    # /* r is in {0,1,2}
    #  * d is in {0,1,2} */

    # /* Accumulate and reduce */
    c = t2
    # c = d[0] & a[0];
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(a[0], d[0], c))
    # a[0] ^= d[0];
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a[0], d[0], a[0]))
    four = d[0]
    # four = a[1] & d[1];
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(a[1], d[1], four))
    # a[1] ^= d[1];
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a[1], d[1], a[1]))
    # a[1] ^= c;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a[1], c, a[1]))

    # a[0] |= four;
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(a[0], four, a[0]))
    # a[1] &= ~four;
    p("vpandn %ymm{}, %ymm{}, %ymm{}".format(a[1], four, a[1]))

    # /* Full reduction */
    t = four
    # t = a[0] & a[1];
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(a[0], a[1], t))
    # a[0] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a[0], t, a[0]))
    # a[1] ^= t;
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a[1], t, a[1]))


if __name__ == '__main__':
    p(".data")
    p(".align 32")

    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")
    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

    p("low16:")
    p(".word 0xFFFF")
    for i in range(15):
        p(".word 0")

    p("const_all_1s:")
    for i in range(16):
        p(".word 0xFFFF")

    p("const_1:")
    p(".word 1")
    for i in range(15):
        p(".word 0")

    p("const_64:")
    p(".word 64")
    for i in range(15):
        p(".word 0")

    p("const_all_but_1:")
    p(".word 0xFFFE")
    for i in range(15):
        p(".word 0xFFFF")

    p("const_high_1:")
    for i in range(15):
        p(".word 0")
    p(".word 0x8000")

    p("const_high_2:")
    for i in range(15):
        p(".word 0")
    p(".word 0xC000")

    p("const_high_4:")
    for i in range(15):
        p(".word 0")
    p(".word 0xF000")

    p("const_high_8:")
    for i in range(15):
        p(".word 0")
    p(".word 0xFF00")

    p("const_high_16:")
    for i in range(15):
        p(".word 0")
    p(".word 0xFFFF")

    p("const_high_32:")
    for i in range(14):
        p(".word 0")
    for i in range(2):
        p(".word 0xFFFF")

    p("const_high_64:")
    for i in range(12):
        p(".word 0x0000")
    for i in range(4):
        p(".word 0xFFFF")

    p("const_high_67:")
    for i in range(11):
        p(".word 0x0000")
    p(".word 0xE000")
    for i in range(4):
        p(".word 0xFFFF")

    p("const_all_but_high_1:")
    for i in range(15):
        p(".word 0xFFFF")
    p(".word 0x7FFF")

    p("const_all_but_high_2:")
    for i in range(15):
        p(".word 0xFFFF")
    p(".word 0x3FFF")

    p("const_all_but_high_4:")
    for i in range(15):
        p(".word 0xFFFF")
    p(".word 0x0FFF")

    p("const_all_but_high_8:")
    for i in range(15):
        p(".word 0xFFFF")
    p(".word 0x00FF")

    p("const_all_but_high_16:")
    for i in range(15):
        p(".word 0xFFFF")
    p(".word 0x0000")

    p("const_all_but_high_32:")
    for i in range(14):
        p(".word 0xFFFF")
    for i in range(2):
        p(".word 0x0000")

    p("const_all_but_high_64:")
    for i in range(12):
        p(".word 0xFFFF")
    for i in range(4):
        p(".word 0x0000")

    p("const_all_but_high_67:")
    for i in range(11):
        p(".word 0xFFFF")
    p(".word 0x1FFF")
    for i in range(4):
        p(".word 0")

    p("const_all_but_high_68:")
    for i in range(11):
        p(".word 0xFFFF")
    p(".word 0x0FFF")
    for i in range(4):
        p(".word 0")

    p("const_all_but_high_70:")
    for i in range(11):
        p(".word 0xFFFF")
    p(".word 0x03FF")
    for i in range(4):
        p(".word 0")

    p("const_all_but_high_74:")
    for i in range(11):
        p(".word 0xFFFF")
    p(".word 0x003F")
    for i in range(4):
        p(".word 0")

    p("const_all_but_high_82:")
    for i in range(10):
        p(".word 0xFFFF")
    p(".word 0x3FFF")
    for i in range(5):
        p(".word 0")

    p("const_all_but_high_98:")
    for i in range(9):
        p(".word 0xFFFF")
    p(".word 0x3FFF")
    for i in range(6):
        p(".word 0")

    p(".text")
    p(".global poly_S3_inv")
    p(".att_syntax prefix")

    p("poly_S3_inv:")

    # can freely use: r8, r9, r10, r11, rax, rcx, rdx
    # others are available as callee-saved; 12, 13, 14
    p("push %r12")
    p("push %r13")
    p("push %r14")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.
    # make room for f, g, b and c
    # bitsliced: [0, 1, 2] are low bits, [3, 4, 5] are high bits
    p("subq ${}, %rsp".format(32 * (6 * 4)))
    f_rsp = 0*32
    g_rsp = 6*32
    b_rsp = 12*32
    c_rsp = 18*32

    ## init f by bitslicing a
    lowmask = 9
    highmask = 'dx'
    p("mov ${}, %r{}".format(int(('0' * 14 + '01') * 4, 2), lowmask))
    p("mov ${}, %r{}".format(int(('0' * 14 + '10') * 4, 2), highmask))
    for i in range(ceil(701 / 64)):
        # accumulate low bits in r10, high bits in r11
        lowreg = 10
        highreg = 11
        p("mov $0, %r{}".format(lowreg))  # can get rid of this by going in reverse
        p("mov $0, %r{}".format(highreg))  # can get rid of this by going in reverse
        for j in range(64 // 4):
            rt0 = 'ax'
            rt1 = 'cx'
            p("mov {}(%rsi), %r{}".format((i*16 + j)*8, rt0))
            if i * 64 + j * 4 == 700:  # zero out anything from x^701 onwards
                p("and low16, %r{}".format(rt0))
            p("pext %r{}, %r{}, %r{}".format(lowmask, rt0, rt1))
            p("pext %r{}, %r{}, %r{}".format(highmask, rt0, rt0))
            if j > 0:
                p("shl ${}, %r{}".format(j * 4, rt1))
                p("shl ${}, %r{}".format(j * 4, rt0))
            p("or %r{}, %r{}".format(rt1, lowreg))
            p("or %r{}, %r{}".format(rt0, highreg))
        p("mov %r{}, {}(%rsp)".format(lowreg, f_rsp + i*8))
        p("mov %r{}, {}(%rsp)".format(highreg, f_rsp + i*8 + 3*32))

    ## init b
    zero = 11
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(zero, zero, zero))
    for i in range(1, 6):
        p("vmovdqa %ymm{}, {}(%rsp)".format(zero, b_rsp + i*32))
    p("mov $1, %r9")
    p("vmovq %r9, %xmm1")
    p("vmovdqa %ymm1, {}(%rsp)".format(b_rsp))

    ## init c
    for i in range(6):
        p("vmovdqa %ymm{}, {}(%rsp)".format(zero, c_rsp + i*32))

    ## init g
    p("vmovdqa const_all_1s, %ymm2")
    for i in range(3, 6):
        p("vmovdqa %ymm{}, {}(%rsp)".format(zero, g_rsp + i*32))
    for i in range(0, 2):
        p("vmovdqa %ymm2, {}(%rsp)".format(g_rsp + i*32))
    p("vmovdqa const_all_but_high_67, %ymm2")
    p("vmovdqa %ymm2, {}(%rsp)".format(g_rsp + 2*32))

    degf = 9  # r9
    degg = 10  # r10
    k = 'ax'  # rax
    notdone = 'dx'  # rdx
    tr0 = 12  # r12
    tr1 = 13  # r13
    tr2 = 14  # r14
    # degrees start at N-1
    p("mov $700, %r{}".format(degf))
    p("mov $700, %r{}".format(degg))
    p("mov $0, %r{}".format(k))
    p("mov $1, %r{}".format(notdone))

    f_regs = [0, 1, 2, 3, 4, 5]
    for i in range(6):
        p("vmovdqa {}(%rsp), %ymm{}".format(f_rsp + i * 32, f_regs[i]))

    #### LOOP
    vt0 = 15
    vt1 = 14
    vt2 = 13  # can maybe eliminate this
    vnotdone = 12
    # not all limbs start out containing non-zero bits, or are used at all
    # TODO come up with tighter bounds;
    # worst case seems to allow 700 + 188 shifts before the high limb
    #   of g is actually guaranteed to be empty, and then an additional
    #   256 for the next limb
    # we only need to start caring about the second limb in c after 256,
    # and then about the third after 512 shifts
    loopbounds = [(256, 3, 1), (256, 3, 2), (700 + 188 - 512, 3, 3),
                  (256, 2, 3), (256, 1, 3)]
    for loopno, (loops, flimbs, climbs) in enumerate(loopbounds):
        p("mov ${}, %ecx".format(loops))
        p("poly_s3_inv_loop_{}:".format(loopno))
        #### This loop should implement:
        # sign = mod3(2 * mod3(g.coeffs[0] * f.coeffs[0]));
        # int sign_notdone = sign & -notdone;
        # swap = (0 - ((degf - degg) >> 63)) && ((sign_notdone / 2) | (sign_notdone % 2));
        # cswappoly(&f, &g, swap);
        # cswappoly(&b, &c, swap);
        # t = (degf ^ degg) & (-swap);
        # degf ^= t;
        # degg ^= t;
        # POLY_S3_FMADD(i, f, g, sign_notdone);
        # POLY_S3_FMADD(i, b, c, sign_notdone);
        # poly_divx(&f, -notdone);
        # poly_mulx(&c, -notdone);
        # degf -= notdone;
        # k += notdone;
        # notdone = (~((degf-1) >> 63)) & 1;
        ####

        # set sign-register's lowest bits
        sign = [10, 11]
        mul_mod3(sign, [g_rsp, g_rsp + 3*32], [f_regs[0], f_regs[3]], t=vt0, a_from_mem=True)
        sign = sign[1], sign[0]  # a bit swap is mul by 2, mod 3

        # now we expand this to the full registers for parallelism
        p("vpand const_1, %ymm{}, %ymm{}".format(sign[0], sign[0]))
        p("vpand const_1, %ymm{}, %ymm{}".format(sign[1], sign[1]))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, vt0, vt0))
        p("vpsubq %ymm{}, %ymm{}, %ymm{}".format(sign[0], vt0, sign[0]))
        p("vpsubq %ymm{}, %ymm{}, %ymm{}".format(sign[1], vt0, sign[1]))
        p("vbroadcastsd %xmm{}, %ymm{}".format(sign[0], sign[0]))
        p("vbroadcastsd %xmm{}, %ymm{}".format(sign[1], sign[1]))

        p("neg %r{}".format(notdone))  # -notdone to expand
        p("vmovq %r{}, %xmm{}".format(notdone, vnotdone))
        p("vbroadcastsd %xmm{}, %ymm{}".format(vnotdone, vnotdone))

        sign_notdone = sign[0], sign[1]
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(sign_notdone[0], vnotdone, sign_notdone[0]))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(sign_notdone[1], vnotdone, sign_notdone[1]))

        swap = 9
        p("vpor %ymm{}, %ymm{}, %ymm{}".format(sign_notdone[0], sign_notdone[1], swap))

        # prepare degf < degg
        degf_c = tr0
        p("mov %r{}, %r{}".format(degf, degf_c))  # copy degf to save original
        p("sub %r{}, %r{}".format(degg, degf_c))  # degf - degg
        p("shr $63, %r{}".format(degf_c))  # set lsb if negative
        p("neg %r{}".format(degf_c))  # expand 1-bit to full register
        p("vmovq %r{}, %xmm{}".format(degf_c, vt2))
        p("vbroadcastsd %xmm{}, %ymm{}".format(vt2, vt2))
        # finish swap
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(vt2, swap, swap))

        # swap degrees
        p("vmovq %xmm{}, %r{}".format(swap, tr0))

        p("mov %r{}, %r{}".format(degf, tr1))
        p("xor %r{}, %r{}".format(degg, tr1))
        p("and %r{}, %r{}".format(tr0, tr1))
        p("xor %r{}, %r{}".format(tr1, degg))
        p("xor %r{}, %r{}".format(tr1, degf))

        # perform cswap(f, g, swap) and cswap(b, c, swap)
        for i in range(flimbs):
            g = [7, 8]
            for j in range(2):
                x = f_regs[i+3*j]
                # t = (x ^ y) & (-swap);
                p("vpxor {}(%rsp), %ymm{}, %ymm{}".format(g_rsp + (i+j*3)*32, x, vt0))
                p("vpand %ymm{}, %ymm{}, %ymm{}".format(swap, vt0, vt0))
                # x ^= t;
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, vt0, x))
                # y ^= t;
                p("vpxor {}(%rsp), %ymm{}, %ymm{}".format(g_rsp + (i+j*3)*32, vt0, g[j]))
                p("vmovdqa %ymm{}, {}(%rsp)".format(g[j], g_rsp + (i+j*3)*32))

            poly_s3_fmadd([f_regs[i], f_regs[i+3]], g, sign_notdone)

        for i in range(climbs):
            b = [6, 7]
            c = [8, vt1]
            for j in range(2):
                x = b[j]
                p("vmovdqa {}(%rsp), %ymm{}".format(b_rsp + (i+j*3)*32, x))
                # t = (x ^ y) & (-swap);
                p("vpxor {}(%rsp), %ymm{}, %ymm{}".format(c_rsp + (i+j*3)*32, x, vt0))
                p("vpand %ymm{}, %ymm{}, %ymm{}".format(swap, vt0, vt0))
                # x ^= t;
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, vt0, x))
                # y ^= t;
                p("vpxor {}(%rsp), %ymm{}, %ymm{}".format(c_rsp + (i+j*3)*32, vt0, c[j]))
                p("vmovdqa %ymm{}, {}(%rsp)".format(c[j], c_rsp + (i+j*3)*32))

            poly_s3_fmadd(b, c, sign_notdone)
            p("vmovdqa %ymm{}, {}(%rsp)".format(b[0], b_rsp + i*32))
            p("vmovdqa %ymm{}, {}(%rsp)".format(b[1], b_rsp + (i+3)*32))

        # do this for both high and low bitsliced bits
        for offset in [0, 3*32]:
            c = [6, 8, 10]
            cout = [7, 9, 11]
            for i in range(climbs):
                p("vmovdqa {}(%rsp), %ymm{}".format(c_rsp + i*32 + offset, c[i]))

            # polymulx(c, vnotdone)
            p("vpsllq $1, %ymm{}, %ymm{}".format(c[0], vt0))
            p("vpsrlq $63, %ymm{}, %ymm{}".format(c[0], vt1))
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt1, cout[0]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, cout[0], cout[0]))
            if climbs >= 2:
                p("vpand const_1, %ymm{}, %ymm{}".format(cout[0], vt2))
            p("vpand const_all_but_1, %ymm{}, %ymm{}".format(cout[0], cout[0]))

            if climbs >= 2:
                p("vpsllq $1, %ymm{}, %ymm{}".format(c[1], vt0))
                p("vpsrlq $63, %ymm{}, %ymm{}".format(c[1], vt1))
                p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt1, cout[1]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, cout[1], cout[1]))
                if climbs >= 2:
                    p("vpand const_1, %ymm{}, %ymm{}".format(cout[1], vt0))
                p("vpand const_all_but_1, %ymm{}, %ymm{}".format(cout[1], cout[1]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, cout[1], cout[1]))  # insert high out from c[0]

            if climbs >= 3:
                p("vpsllq $1, %ymm{}, %ymm{}".format(c[2], vt2))
                p("vpsrlq $63, %ymm{}, %ymm{}".format(c[2], vt1))
                p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt1, cout[2]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, cout[2], cout[2]))
                p("vpand const_all_but_1, %ymm{}, %ymm{}".format(cout[2], cout[2]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, cout[2], cout[2]))  # insert high out from c[1]

            # now we do half a cswap with c using vnotdone as signal
            for i in range(climbs):
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(c[i], cout[i], vt0))
                p("vpand %ymm{}, %ymm{}, %ymm{}".format(vnotdone, vt0, vt0))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(c[i], vt0, c[i]))
                p("vmovdqa %ymm{}, {}(%rsp)".format(c[i], c_rsp + i*32 + offset))

            # polydivx(f, vnotdone)
            f = [f_regs[i + offset//32] for i in range(3)]
            fout = [6, 7, 8]

            if flimbs >= 3:
                p("vpsrlq $1, %ymm{}, %ymm{}".format(f[2], vt0))
                p("vpsllq $63, %ymm{}, %ymm{}".format(f[2], vt1))
                p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, fout[2]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, fout[2], fout[2]))
                p("vpand const_high_1, %ymm{}, %ymm{}".format(fout[2], vt2))
                p("vpand const_all_but_high_67, %ymm{}, %ymm{}".format(fout[2], fout[2]))

            if flimbs >= 2:
                p("vpsrlq $1, %ymm{}, %ymm{}".format(f[1], vt0))
                p("vpsllq $63, %ymm{}, %ymm{}".format(f[1], vt1))
                p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, fout[1]))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, fout[1], fout[1]))
                p("vpand const_high_1, %ymm{}, %ymm{}".format(fout[1], vt0))
                p("vpand const_all_but_high_1, %ymm{}, %ymm{}".format(fout[1], fout[1]))
            if flimbs >= 3:
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, fout[1], fout[1]))  # insert high out from f[2]

            p("vpsrlq $1, %ymm{}, %ymm{}".format(f[0], vt2))
            p("vpsllq $63, %ymm{}, %ymm{}".format(f[0], vt1))
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, fout[0]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, fout[0], fout[0]))
            p("vpand const_all_but_high_1, %ymm{}, %ymm{}".format(fout[0], fout[0]))
            if flimbs >= 2:
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, fout[0], fout[0]))  # insert high out from f[1]

            # now we do half a cswap with f using vnotdone as signal
            for i in range(flimbs):
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(f[i], fout[i], vt0))
                p("vpand %ymm{}, %ymm{}, %ymm{}".format(vnotdone, vt0, vt0))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(f[i], vt0, f[i]))

        p("add %r{}, %r{}".format(notdone, degf))  # notdone contains -1
        p("sub %r{}, %r{}".format(notdone, k))

        # notdone = (~((degf-1) >> 63)) & 1;
        p("mov %r{}, %r{}".format(degf, notdone))
        p("sub $1, %r{}".format(notdone))
        p("shr $63, %r{}".format(notdone))
        p("not %r{}".format(notdone))
        p("and $1, %r{}".format(notdone, notdone))

        p("dec %ecx")
        p("jns poly_s3_inv_loop_{}".format(loopno))

    ###################### ENDLOOP ######################

    f_low = [f_regs[0], f_regs[3]]

    # expand the low bit of f to all bits
    p("vpand const_1, %ymm{}, %ymm{}".format(f_low[0], f_low[0]))
    p("vpand const_1, %ymm{}, %ymm{}".format(f_low[1], f_low[1]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, vt0, vt0))
    p("vpsubq %ymm{}, %ymm{}, %ymm{}".format(f_low[0], vt0, f_low[0]))
    p("vpsubq %ymm{}, %ymm{}, %ymm{}".format(f_low[1], vt0, f_low[1]))
    p("vbroadcastsd %xmm{}, %ymm{}".format(f_low[0], f_low[0]))
    p("vbroadcastsd %xmm{}, %ymm{}".format(f_low[1], f_low[1]))

    # multiply with b
    b_regs = [6, 7, 8, 9, 10, 11]
    r = [12, 13]
    for i in range(6):
        p("vmovdqa {}(%rsp), %ymm{}".format(b_rsp + i*32, b_regs[i]))

    for i in range(3):
        mul_mod3(r, [b_regs[i], b_regs[i+3]], f_low)
        b_regs[i], r[0] = r[0], b_regs[i]
        b_regs[i+3], r[1] = r[1], b_regs[i+3]

    for i in range(6):
        p("vmovdqa  %ymm{}, {}(%rsp)".format(b_regs[i], b_rsp + i*32))
    # k = k - NTRU_N*(k >= NTRU_N);
    flag = tr2
    k_backup = tr0
    p("mov %r{}, %r{}".format(k, k_backup))  # copy k
    p("sub $702, %r{}".format(k))  # k - 702 is negative if k >= NTRU_N
    p("mov %r{}, %r{}".format(k, tr1))  # copy reduced k
    p("add $1, %r{}".format(k))  # actually correctly reduce k
    p("shr $63, %r{}".format(tr1))  # set lsb if negative
    p("xor %r{}, %r{}".format(flag, flag))
    p("sub %r{}, %r{}".format(tr1, flag))  # expand 1-bit to full register

    tr3 = notdone
    # cmov depending on bits in tr1
    p("mov %r{}, %r{}".format(k, tr3))  # copy reduced k
    p("xor %r{}, %r{}".format(k_backup, k))
    p("and %r{}, %r{}".format(flag, k))  # if set, we need to restore k
    p("xor %r{}, %r{}".format(tr3, k))

    # now we rotate according to the set bits in k (so log(701) rotates)
    # this is going to be a bit painful, because each rotation is subtly different
    vksignal = vnotdone  # 7
    vk = 10
    zero = 11
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(zero, zero, zero))
    for offset in [0, 3*32]:
        b = [3, 4, 5]
        bout = [0, 1, 2]
        for i in range(3):
            p("vmovdqa {}(%rsp), %ymm{}".format(b_rsp + i*32 + offset, b[i]))

        def cmov_b_vksignal():
            p("vpand const_1, %ymm{}, %ymm{}".format(vk, vksignal))
            p("vpsubq %ymm{}, %ymm{}, %ymm{}".format(vksignal, zero, vksignal))
            p("vbroadcastsd %xmm{}, %ymm{}".format(vksignal, vksignal))
            for i in range(3):
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(b[i], bout[i], vt0))
                p("vpand %ymm{}, %ymm{}, %ymm{}".format(vksignal, vt0, vt0))
                p("vpxor %ymm{}, %ymm{}, %ymm{}".format(b[i], vt0, b[i]))

        # now we have the data, we do the rotations

        # reset k
        for r in [1, 2, 4, 8, 16, 32]:
             ## ROTATION FOR r BITS
            p("vpsrlq ${}, %ymm{}, %ymm{}".format(r, b[2], vt0))
            p("vpsllq ${}, %ymm{}, %ymm{}".format(64-r, b[2], vt1))
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, bout[2]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[2], bout[2]))
            p("vpand const_high_{}, %ymm{}, %ymm{}".format(r, bout[2], vt2))
            p("vpand const_all_but_high_{}, %ymm{}, %ymm{}".format(66+r, bout[2], bout[2]))

            p("vpsrlq ${}, %ymm{}, %ymm{}".format(r, b[1], vt0))
            p("vpsllq ${}, %ymm{}, %ymm{}".format(64-r, b[1], vt1))
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, bout[1]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[1], bout[1]))
            p("vpand const_high_{}, %ymm{}, %ymm{}".format(r, bout[1], vt0))
            p("vpand const_all_but_high_{}, %ymm{}, %ymm{}".format(r, bout[1], bout[1]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, bout[1], bout[1]))  # insert high out from b[2]

            p("vpsrlq ${}, %ymm{}, %ymm{}".format(r, b[0], vt2))
            p("vpsllq ${}, %ymm{}, %ymm{}".format(64-r, b[0], vt1))
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt1, bout[0]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, bout[0], bout[0]))
            p("vpand const_high_{}, %ymm{}, %ymm{}".format(r, bout[0], vt2))
            p("vpand const_all_but_high_{}, %ymm{}, %ymm{}".format(r, bout[0], bout[0]))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[0], bout[0]))  # insert high out from b[1]

            # the high bits we want to insert needs to be moved 67 places down
            p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt2, vt2))
            p("vpsrlq $3, %ymm{}, %ymm{}".format(vt2, vt2))
            p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt2, bout[2], bout[2]))  # insert high out from b[0] back into b[2]

            # now we do a cmov of bout using vksignal as signal
            if r == 1:
                p("vmovq %r{}, %xmm{}".format(k, vk))
            else:
                p("vpsrlq $1, %ymm{}, %ymm{}".format(vk, vk))
            cmov_b_vksignal()

        # the next few rotations are not really suited for a generic approach
        # ROTATE RIGHT BY 64 BITS
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), b[2], vt0))
        p("vpand const_high_64, %ymm{}, %ymm{}".format(vt0, vt1))
        p("vpand const_all_but_high_64, %ymm{}, %ymm{}".format(vt0, bout[2]))

        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), b[1], vt0))
        p("vpand const_high_64, %ymm{}, %ymm{}".format(vt0, vt2))
        p("vpand const_all_but_high_64, %ymm{}, %ymm{}".format(vt0, bout[1]))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bout[1], vt1, bout[1]))  # insert high out from b[2]

        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), b[0], vt0))
        p("vpand const_high_64, %ymm{}, %ymm{}".format(vt0, vt1))
        p("vpand const_all_but_high_64, %ymm{}, %ymm{}".format(vt0, bout[1]))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bout[0], vt2, bout[0]))  # insert high out from b[1]

        # high bits we want to insert need to be spread across the xmm lane..
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt2, vt1))
        p("vpsrlq $3, %ymm{}, %ymm{}".format(vt1, vt1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, bout[2], bout[2]))  # insert high out from b[0] back into b[2]

        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01001110', 2), vt2, vt1))
        p("vpsllq $61, %ymm{}, %ymm{}".format(vt1, vt1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, bout[2], bout[2]))  # insert high out from b[0] back into b[2]

        # now we do a cmov of bout using vksignal as signal
        p("vpsrlq $1, %ymm{}, %ymm{}".format(vk, vk))
        cmov_b_vksignal()

        # ROTATE RIGHT BY 128 BITS
        p("vextracti128 $0, %ymm{}, %xmm{}".format(b[0], vt0))
        p("vextracti128 $1, %ymm{}, %xmm{}".format(b[0], bout[0]))
        p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(b[1], bout[0], bout[0]))
        p("vextracti128 $1, %ymm{}, %xmm{}".format(b[1], bout[1]))
        p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(b[2], bout[1], bout[1]))
        p("vextracti128 $1, %ymm{}, %xmm{}".format(b[2], bout[2]))
        # insert low 128 into the emptied spots in bout[2]
        p("vpsllq ${}, %ymm{}, %ymm{}".format(61, vt0, vt1))
        p("vpsrlq ${}, %ymm{}, %ymm{}".format(3, vt0, vt2))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt2, vt0))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, vt0, vt0))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[2], bout[2]))

        # now we do a cmov of bout using vksignal as signal
        p("vpsrlq $1, %ymm{}, %ymm{}".format(vk, vk))
        cmov_b_vksignal()

        # ROTATE RIGHT BY 256 BITS
        # still perform the moves just for sanity; can get rid of this by modifying cmov
        p("vmovdqa %ymm{}, %ymm{}".format(b[1], bout[0]))
        p("vmovdqa %ymm{}, %ymm{}".format(b[2], bout[1]))

        # rotate lowest 67 bits of b[0] into highest 67 of bout[1]
        # and the high 189 into low of bout[2]
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), b[0], vt0))  # that's 64
        p("vpsrlq ${}, %ymm{}, %ymm{}".format(3, vt0, vt1))
        p("vpsllq ${}, %ymm{}, %ymm{}".format(61, vt0, vt2))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('00111001', 2), vt2, vt0))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, vt0, vt0))
        p("vpand const_all_but_high_67, %ymm{}, %ymm{}".format(vt0, bout[2]))
        p("vpand const_high_67, %ymm{}, %ymm{}".format(vt0, vt0))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[1], bout[1]))

        p("vpsrlq $1, %ymm{}, %ymm{}".format(vk, vk))
        cmov_b_vksignal()

        # ROTATE RIGHT BY 512 BITS
        # but it's easier to rotate left by 189 (= 128 + 61) bits
        # still perform move just for sanity; can get rid of this by modifying cmov
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01001110', 2), b[0], bout[0]))  # that's 128
        p("vpsllq ${}, %ymm{}, %ymm{}".format(61, bout[0], vt1))
        p("vpsrlq ${}, %ymm{}, %ymm{}".format(3, bout[0], vt2))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt2, vt2))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, vt2, bout[0]))
        p("vpand const_all_but_high_67, %ymm{}, %ymm{}".format(bout[0], vt0))
        p("vpand const_high_67, %ymm{}, %ymm{}".format(bout[0], bout[0]))

        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01001110', 2), b[1], bout[2]))  # that's 128
        p("vpsllq ${}, %ymm{}, %ymm{}".format(61, bout[2], vt1))
        p("vpsrlq ${}, %ymm{}, %ymm{}".format(3, bout[2], vt2))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), vt2, vt2))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt1, vt2, bout[2]))
        p("vpand const_high_67, %ymm{}, %ymm{}".format(bout[2], bout[1]))
        p("vpand const_all_but_high_67, %ymm{}, %ymm{}".format(bout[2], bout[2]))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(vt0, bout[1], bout[1]))

        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(b[2], bout[0], bout[0]))

        p("vpsrlq $1, %ymm{}, %ymm{}".format(vk, vk))
        cmov_b_vksignal()

        # now we have the rotated data, we write it out
        for i in range(3):
            p("vmovdqa %ymm{}, {}(%rsp)".format(b[i], b_rsp + i*32 + offset))

    # unbitslice b
    lowmask = 9
    highmask = 'dx'
    p("mov ${}, %r{}".format(int(('0' * 14 + '01') * 4, 2), lowmask))
    p("mov ${}, %r{}".format(int(('0' * 14 + '10') * 4, 2), highmask))
    for i in range(ceil(701 / 64)):
        # get low bits
        lowreg = 10
        highreg = 11
        p("mov {}(%rsp), %r{}".format(b_rsp + i*8, lowreg))
        p("mov {}(%rsp), %r{}".format(b_rsp + i*8 + 3*32, highreg))
        for j in range(64 // 4):
            if j > 0:
                p("shr ${}, %r{}".format(4, lowreg))
                p("shr ${}, %r{}".format(4, highreg))
            t0 = 12
            t1 = 13
            p("pdep %r{}, %r{}, %r{}".format(lowmask, lowreg, t0))
            p("pdep %r{}, %r{}, %r{}".format(highmask, highreg, t1))
            combined = t1
            p("or %r{}, %r{}".format(t0, t1))
            p("mov %r{}, {}(%rdi)".format(combined, (i*16 + j)*8))


    # Account for lazy reduction of Sq to Sp;
    # for(i=0; i<NTRU_N; i++)
    #     r->coeffs[i] = mod3(r->coeffs[i] + 2*r->coeffs[NTRU_N-1]);

    N_min_1 = 0
    t = 1
    # NTRU_N is in 701th element; 13th word of 44th register
    p("vmovdqa {}(%rdi), %ymm{}".format(43*32, N_min_1))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00000011', 2), N_min_1, N_min_1))
    # move into high 16 in doubleword (to clear high 16) and multiply by two
    p("vpslld $17, %ymm{}, %ymm{}".format(N_min_1, N_min_1))
    # clone into bottom 16
    p("vpsrld $16, %ymm{}, %ymm{}".format(N_min_1, t))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(N_min_1, t, N_min_1))
    # and now it's everywhere in N_min_1
    p("vbroadcastss %xmm{}, %ymm{}".format(N_min_1, N_min_1))

    retval = 2
    for i in range(ceil(701 / 16)):
        p("vpaddw {}(%rdi), %ymm{}, %ymm{}".format(i * 32, N_min_1, t))
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, i*32))

    p("mov %r8, %rsp")
    p("pop %r14")
    p("pop %r13")
    p("pop %r12")
    p("ret")
