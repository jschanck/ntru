from math import ceil

from params import *

p = print


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


if __name__ == '__main__':
    p(".data")
    p(".p2align 5")

    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")
    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

    p("coeff_0:")
    p(".word 0xFFFF")
    for i in range(15):
        p(".word 0")

    p("coeff_1:")
    p(".word 0")
    p(".word 0xFFFF")
    for i in range(14):
        p(".word 0")

    p("coeff_2:")
    for i in range(2):
        p(".word 0")
    p(".word 0xFFFF")
    for i in range(13):
        p(".word 0")

    p("mask100:")
    for i in range(16):
        p(".word", "0xFFFF" if i % 3 == 0 else "0")

    p("mask010:")
    for i in range(16):
        p(".word", "0xFFFF" if i % 3 == 1 else "0")

    p("mask001:")
    for i in range(16):
        p(".word", "0xFFFF" if i % 3 == 2 else "0")

    p("mask100_701:")
    for i in range(13):
        p(".word", "0xFFFF" if i % 3 == 0 else "0")
    for i in range(3):
        p(".word 0")

    p("mask010_701:")
    for i in range(13):
        p(".word", "0xFFFF" if i % 3 == 1 else "0")
    for i in range(3):
        p(".word 0")

    p("mask001_701:")
    for i in range(13):
        p(".word", "0xFFFF" if i % 3 == 2 else "0")
    for i in range(3):
        p(".word 0")

    p("shuf_128_to_64:")
    for i in range(8):
        p(".byte", i+8)
    for i in range(24):
        p(".byte 255")

    p("const_1s:")
    for i in range(16):
        p(".word 1")

    p("const_8191s:")
    for i in range(16):
        p(".word 8191")

    p("mask_701:")
    for i in range(13):
        p(".word 0xFFFF")
    for i in range(3):
        p(".word 0")

    p(".text")
    p(".global poly_lift")
    p(".global _poly_lift")

    p("poly_lift:")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.
    p("subq ${}, %rsp".format(32 * ceil(701 / 16)))

    zero = 0
    a = 1
    b = [2, 3, 4]
    t = 5

    # b.coeffs[0] = - a->coeffs[0];
    # b.coeffs[1] = - a->coeffs[1] - a->coeffs[0];
    # b.coeffs[2] = - a->coeffs[2] - a->coeffs[1] - a->coeffs[0];
    p("vmovdqa {}(%rsi), %ymm{}".format(0, a))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(zero, zero, zero))
    p("vpand coeff_0, %ymm{}, %ymm{}".format(a, t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[0]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[1]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[2]))
    p("vpand coeff_1, %ymm{}, %ymm{}".format(a, t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpand coeff_2, %ymm{}, %ymm{}".format(a, t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))

    masks = ['100', '010', '001']

    # for(i=0; i<NTRU_N; i++) {
    #    b.coeffs[0] += a->coeffs[i] * ((i + 2)%3);
    #    b.coeffs[1] += a->coeffs[i] * ((i + 1)%3);
    #    b.coeffs[2] += a->coeffs[i] * (i%3);
    # }
    # TODO what if we move the masks into registers first
    for i in range(ceil(701 / 16)):
        if i == ceil(701 / 16) - 1:
            masks = ['100_701', '010_701', '001_701']
        p("vmovdqa {}(%rsi), %ymm{}".format((i*16) * 2, a))

        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(2 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(0 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))

        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(0 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(1 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))

        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(1 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
        p("vpand mask{}, %ymm{}, %ymm{}".format(masks[(2 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))

    # combine b[0], b[1], b[2]

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpshufb shuf_128_to_64, %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpsrlq $32, %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpsrlq $16, %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpand coeff_0, %ymm{}, %ymm{}".format(b[0], b[0]))

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpshufb shuf_128_to_64, %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsrlq $32, %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsllq $16, %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpand coeff_1, %ymm{}, %ymm{}".format(b[1], b[1]))

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpshufb shuf_128_to_64, %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpsllq $32, %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpsrlq $16, %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpand coeff_2, %ymm{}, %ymm{}".format(b[2], b[2]))

    p("vpor %ymm{}, %ymm{}, %ymm{}".format(b[0], b[1], t))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(t, b[2], t))
    p("vmovdqa %ymm{}, {}(%rsp)".format(t, 0))

    a = 1
    b = 2
    bmin3 = 3
    amin1 = 4
    amin2 = 5

    # for(i=3; i<NTRU_N; i++)
    #   b.coeffs[i] = 2*(a->coeffs[i] + a->coeffs[i-1] + a->coeffs[i-2]);

    for i in range(ceil(701 / 16) - 1):
        p("vmovdqu {}(%rsi), %ymm{}".format((3 + i*16) * 2, a))
        p("vmovdqu {}(%rsi), %ymm{}".format((2 + i*16) * 2, amin1))
        p("vmovdqu {}(%rsi), %ymm{}".format((1 + i*16) * 2, amin2))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin1, a, a))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin2, a, a))
        p("vpsllw $1, %ymm{}, %ymm{}".format(a, b))
        p("vmovdqu %ymm{}, {}(%rsp)".format(b, 2*(3 + i*16)))

    # from 691 to 701 we cannot use the same loop, as we would exceed bounds
    p("vmovdqa {}(%rsi), %ymm{}".format((0 + 43*16) * 2, a))
    p("vpand mask_701, %ymm{}, %ymm{}".format(a, a))
    p("vmovdqu {}(%rsi), %ymm{}".format((-1 + 43*16) * 2, amin1))
    p("vmovdqu {}(%rsi), %ymm{}".format((-2 + 43*16) * 2, amin2))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin1, a, a))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin2, a, a))
    p("vpsllw $1, %ymm{}, %ymm{}".format(a, b))
    p("vmovdqa %ymm{}, {}(%rsp)".format(b, 2*(43*16)))

    # for(i=3; i<NTRU_N; i++)
    #   b.coeffs[i] += b.coeffs[i-3]
    p("movq {}(%rsp), %r9".format(0))
    p("movq {}(%rsp), %r10".format(3 * 2))
    regs = ['r9', 'r10', 'r11']
    for i in range(1, ceil(701 / 3)):
        p("add %{}, %{}".format(regs[0], regs[1]))
        if i != ceil(701 / 3) - 1:
            p("movq {}(%rsp), %{}".format((i+1) * 3 * 2, regs[2]))
        p("movq %{}, {}(%rsp)".format(regs[1], i * 3 * 2))
        regs = regs[1:3] + [regs[0]]

    # for(i=0; i<NTRU_N; i++)
    #     b.coeffs[i] = mod3(b.coeffs[i] + 2*b.coeffs[NTRU_N-1]);
    N_min_1 = 1
    t = 2
    # NTRU_N is in 701th element; 13th word of 44th register
    p("vmovdqa {}(%rsp), %ymm{}".format(43*32, N_min_1))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00000011', 2), N_min_1, N_min_1))
    # move into high 16 in doubleword (to clear high 16) and multiply by two
    p("vpslld $17, %ymm{}, %ymm{}".format(N_min_1, N_min_1))
    # clone into bottom 16
    p("vpsrld $16, %ymm{}, %ymm{}".format(N_min_1, t))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(N_min_1, t, N_min_1))
    # and now it's everywhere in N_min_1
    p("vbroadcastss %xmm{}, %ymm{}".format(N_min_1, N_min_1))

    retval = 3
    t2 = 4
    for i in range(ceil(701 / 16)):
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(i * 32, N_min_1, t))
        mod3(t, retval)
        # b.coeffs[i] = ZP_TO_ZQ(b.coeffs[i]);
        p("vpsrlq $1, %ymm{}, %ymm{}".format(retval, t))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, t))
        p("vpand const_8191s, %ymm{}, %ymm{}".format(t, t))
        p("vpand const_1s, %ymm{}, %ymm{}".format(retval, retval))
        p("vpor %ymm{}, %ymm{}, %ymm{}".format(retval, t, retval))
        p("vmovdqa %ymm{}, {}(%rsp)".format(retval, i*32))

    p("mov %rsp, %rsi")  # use b as input for poly_Rq_mul_x_minus_1
    p("call poly_Rq_mul_x_minus_1")

    p("mov %r8, %rsp")
    p("ret")
