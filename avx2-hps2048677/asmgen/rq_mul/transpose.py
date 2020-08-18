
p = print


def _transpose_16x16_to_16x16(dst, src, src_off=0, dst_off=0, src_gap=3, dst_gap=1, dst_limit=None):
    s = [0, None, 1, None, 2, None, 3, None]
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(0*2)+src_off), src, s[0]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(1*2)+src_off), src, s[2]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(2*2)+src_off), src, s[4]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(3*2)+src_off), src, s[6]))

    t = list(range(4,12)) + [None] * 8
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*1+src_off), src, s[0], t[0]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*1+src_off), src, s[0], t[1]))
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*3+src_off), src, s[2], t[2]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*3+src_off), src, s[2], t[3]))
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*5+src_off), src, s[4], t[4]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*5+src_off), src, s[4], t[5]))
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*7+src_off), src, s[6], t[6]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*7+src_off), src, s[6], t[7]))

    r = list(range(0,4)) + list(range(12, 16))
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[2], t[0], r[0]))
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[2], t[0], r[1]))
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[3], t[1], r[2]))
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[3], t[1], r[3]))
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[6], t[4], r[4]))
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[6], t[4], r[5]))
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[7], t[5], r[6]))
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[7], t[5], r[7]))

    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[4], r[0], t[0]))
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[4], r[0], t[1]))
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[5], r[1], t[2]))
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[5], r[1], t[3]))
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[6], r[2], t[4]))
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[6], r[2], t[5]))
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[7], r[3], t[6]))
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[7], r[3], t[7]))

    # this is where it gets nasty because we only have 16 registers
    t[8:12] = [12, 13, 14, 15]
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(4*2)+src_off), src, s[0]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(5*2)+src_off), src, s[2]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(6*2)+src_off), src, s[4]))
    p("vmovdqa {}({}), %ymm{}".format(32*(src_gap*(7*2)+src_off), src, s[6]))

    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*9+src_off), src, s[0], t[8]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*9+src_off), src, s[0], t[9]))
    t[12] = s[0]
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*11+src_off), src, s[2], t[10]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*11+src_off), src, s[2], t[11]))
    t[13] = s[2]
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*13+src_off), src, s[4], t[12]))
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*13+src_off), src, s[4], t[13]))
    t[14] = s[4]
    p("vpunpcklwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*15+src_off), src, s[6], t[14]))
    t[15] = s[6]  # this is a super tight fit, but it still works out
    p("vpunpckhwd {}({}), %ymm{}, %ymm{}".format(32*(src_gap*15+src_off), src, s[6], t[15]))

    # .. but now we really do need extra storage space
    p("vmovdqa %ymm{}, 0(%rsp)".format(t[7]))
    r[0] = t[7]

    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[10], t[8], r[0]))
    r[1] = t[8]  # .. and it's still continuously a tight squeeze
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[10], t[8], r[1]))
    r[2] = t[10]
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[11], t[9], r[2]))
    r[3] = t[11]
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[11], t[9], r[3]))
    r[4] = t[9]
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[14], t[12], r[4]))
    r[5] = t[12]
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[14], t[12], r[5]))
    r[6] = t[14]
    p("vpunpckldq %ymm{}, %ymm{}, %ymm{}".format(t[15], t[13], r[6]))
    r[7] = t[13]
    p("vpunpckhdq %ymm{}, %ymm{}, %ymm{}".format(t[15], t[13], r[7]))

    t[8] = t[15]
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[4], r[0], t[8]))
    t[9] = r[4]
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[4], r[0], t[9]))
    t[10] = r[0]
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[5], r[1], t[10]))
    t[11] = r[5]
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[5], r[1], t[11]))
    t[12] = r[1]
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[6], r[2], t[12]))
    t[13] = r[6]
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[6], r[2], t[13]))
    t[14] = r[2]
    p("vpunpcklqdq %ymm{}, %ymm{}, %ymm{}".format(r[7], r[3], t[14]))
    t[15] = r[7]
    p("vpunpckhqdq %ymm{}, %ymm{}, %ymm{}".format(r[7], r[3], t[15]))
    # now r[3] is free, t[7] is still in memory
    free = r[3]

    for i in range(7):  # t[7] is tricky
        p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(t[8+i], t[i], free))
        p("vmovdqa %ymm{}, {}({})".format(free, 32*(dst_gap*i+dst_off), dst))

    for i in range(7):  # t[7] still tricky
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01001110', 2), t[i], t[i]))

    for i in range(8, 15):  # t[7] is tricky
        if dst_limit is None or i < dst_limit:
            p("vinserti128 $0, %xmm{}, %ymm{}, %ymm{}".format(t[i-8], t[i], free))
            p("vmovdqa %ymm{}, {}({})".format(free, 32*(dst_gap*i+dst_off), dst))

    p("vmovdqa 0(%rsp), %ymm{}".format(t[7]))
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(t[15], t[7], t[14]))
    p("vmovdqa %ymm{}, {}({})".format(t[14], 32*(dst_gap*7+dst_off), dst))

    if dst_limit is None or 15 < dst_limit:
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01001110', 2), t[7], t[7]))
        p("vinserti128 $0, %xmm{}, %ymm{}, %ymm{}".format(t[7], t[15], t[15]))
        p("vmovdqa %ymm{}, {}({})".format(t[15], 32*(dst_gap*15+dst_off), dst))


def transpose_48x16_to_16x44(dst, src, src_off=0, dst_off=0):
    p("subq $32, %rsp")
    if src == '%rsp':
        src_off += 1
    if dst == '%rsp':
        dst_off += 1
    for n in range(3):
        dst_limit = 12 if n == 2 else None
        _transpose_16x16_to_16x16(dst, src, src_off=n+src_off,
                                  dst_off=dst_off+n*16,
                                  src_gap=3, dst_limit=dst_limit)
    p("addq $32, %rsp")


def transpose_16x96_to_96x16(dst, src, src_off=0, dst_off=0):
    """ It turns out to be tricky to make this 16x88 to 96x16 because of
        divisibility in 32-byte blocks. """
    p("subq $32, %rsp")
    if src == '%rsp':
        src_off += 1
    if dst == '%rsp':
        dst_off += 1
    for n in range(6):
        # artificially create a gap after every 44 coefficients
        # this is very useful when interpolating multiple outputs in Karatsuba
        gap44 = 0 if n < 3 else 4
        _transpose_16x16_to_16x16(dst, src, src_off=src_off+n*16-gap44, dst_off=dst_off+n,
                                  src_gap=1, dst_gap=6)
    p("addq $32, %rsp")


if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".p2align 5")

    p(".text")
    p(".global transpose_48x16_to_16x44")
    p(".global _transpose_48x16_to_16x44")
    p(".global transpose_48x16_to_16x44_stackbased")
    p(".global _transpose_48x16_to_16x44_stackbased")
    p(".global transpose_16x96_to_96x16")
    p(".global _transpose_16x96_to_96x16")
    p(".global transpose_16x96_to_96x16_stackbased")
    p(".global _transpose_16x96_to_96x16_stackbased")

    p("transpose_48x16_to_16x44:")
    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    transpose_48x16_to_16x44('%rdi', '%rsi')

    p("mov %r8, %rsp")
    p("ret")

    p("transpose_16x96_to_96x16:")
    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    transpose_16x96_to_96x16('%rdi', '%rsi')

    p("mov %r8, %rsp")
    p("ret")

    p("transpose_48x16_to_16x44_stackbased:")
    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    p("subq ${}, %rsp".format(32 * (37 + 44)))  # allocate some stack space
    dst_off = 37
    transpose_48x16_to_16x44(dst='%rsp', src='%rsi', dst_off=dst_off)
    for i in range(44):
        p("vmovdqa {}(%rsp), %ymm0".format((i+dst_off)*32))
        p("vmovdqa %ymm0, {}(%rdi)".format(i*32))

    p("mov %r8, %rsp")
    p("ret")

    p("transpose_16x96_to_96x16_stackbased:")
    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    p("subq ${}, %rsp".format(32 * (11 + 96)))  # allocate some stack space
    src_off = 11
    for i in range(96):
        p("vmovdqa {}(%rsi), %ymm0".format(i*32))
        p("vmovdqa %ymm0, {}(%rsp)".format((i + src_off)*32))
    transpose_16x96_to_96x16(dst='%rdi', src='%rsp', src_off=src_off)

    p("mov %r8, %rsp")
    p("ret")
