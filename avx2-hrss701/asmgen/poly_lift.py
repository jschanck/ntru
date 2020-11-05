p = print

from params import *
from mod3 import mod3, mod3_masks
from math import ceil


if __name__ == '__main__':
    p(".data")
    p(".p2align 5")

    mod3_masks()

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

    p("const_modq:")
    for i in range(16):
        p(".word {}".format(NTRU_Q-1))

    p("mask_n:")
    for i in range(13):
        p(".word 0xFFFF")
    for i in range(3):
        p(".word 0")

    p("mask_omit_lowest:")
    p(".word 0")
    for i in range(15):
        p(".word 0xFFFF")

    p("shuf_5_to_0_zerorest:")
    for i in range(2):
        p(".byte {}".format((i + 2*5) % 16))
    for i in range(30):
        p(".byte 255")

    p(".text")
    p(".global {}poly_lift".format(NAMESPACE))
    p(".global _{}poly_lift".format(NAMESPACE))

    p("{}poly_lift:".format(NAMESPACE))
    p("_{}poly_lift:".format(NAMESPACE))

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.
    p("subq ${}, %rsp".format(32 * ceil(NTRU_N / 16)))

    zero = 0
    a = 1
    b = [2, 3, 4]
    t = 5

    # b.coeffs[0] = - a->coeffs[0];
    # b.coeffs[1] = - a->coeffs[1] - a->coeffs[0];
    # b.coeffs[2] = - a->coeffs[2] - a->coeffs[1] - a->coeffs[0];
    p("vmovdqa {}(%rsi), %ymm{}".format(0, a))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(zero, zero, zero))
    p("vpand coeff_0(%rip), %ymm{}, %ymm{}".format(a, t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[0]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[1]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, zero, b[2]))
    p("vpand coeff_1(%rip), %ymm{}, %ymm{}".format(a, t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpand coeff_2(%rip), %ymm{}, %ymm{}".format(a, t))
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

        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(2 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(0 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))

        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(0 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(1 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))

        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(1 - i) % 3], a, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
        p("vpand mask{}(%rip), %ymm{}, %ymm{}".format(masks[(2 - i) % 3], a, t))
        p("vpsllw $1, %ymm{}, %ymm{}".format(t, t))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))

    # combine b[0], b[1], b[2]

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpshufb shuf_128_to_64(%rip), %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpsrlq $32, %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpsrlq $16, %ymm{}, %ymm{}".format(b[0], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[0], b[0]))
    p("vpand coeff_0(%rip), %ymm{}, %ymm{}".format(b[0], b[0]))

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpshufb shuf_128_to_64(%rip), %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsrlq $32, %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpsllq $16, %ymm{}, %ymm{}".format(b[1], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[1], b[1]))
    p("vpand coeff_1(%rip), %ymm{}, %ymm{}".format(b[1], b[1]))

    p("vextracti128 $1, %ymm{}, %xmm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpshufb shuf_128_to_64(%rip), %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpsllq $32, %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpsrlq $16, %ymm{}, %ymm{}".format(b[2], t))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t, b[2], b[2]))
    p("vpand coeff_2(%rip), %ymm{}, %ymm{}".format(b[2], b[2]))

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

    for i in range(ceil(NTRU_N / 16) - 1):
        p("vmovdqu {}(%rsi), %ymm{}".format((3 + i*16) * 2, a))
        p("vmovdqu {}(%rsi), %ymm{}".format((2 + i*16) * 2, amin1))
        p("vmovdqu {}(%rsi), %ymm{}".format((1 + i*16) * 2, amin2))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin1, a, a))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(amin2, a, a))
        p("vpsllw $1, %ymm{}, %ymm{}".format(a, b))
        p("vmovdqu %ymm{}, {}(%rsp)".format(b, 2*(3 + i*16)))

    # from 691 to 701 we cannot use the same loop, as we would exceed bounds
    p("vmovdqa {}(%rsi), %ymm{}".format((0 + 43*16) * 2, a))
    p("vpand mask_n(%rip), %ymm{}, %ymm{}".format(a, a))
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
        p("vpand const_modq(%rip), %ymm{}, %ymm{}".format(t, t))
        p("vpor %ymm{}, %ymm{}, %ymm{}".format(retval, t, retval))
        p("vmovdqa %ymm{}, {}(%rsp)".format(retval, i*32))

    a_imin1 = 0
    t0 = 1
    t1 = 4
    for i in range(ceil(701 / 16)-1, 0, -1):
        p("vmovdqu {}(%rsp), %ymm{}".format((i*16 - 1) * 2, a_imin1))
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(i * 32, a_imin1, t0))
        p("vmovdqa %ymm{}, {}(%rdi)".format(t0, i*32))
        if i == ceil(701 / 16)-1:
            # a_imin1 now contains 687 to 702 inclusive;
            # we need 700 for [0], which is at position 14
            p("vextracti128 $1, %ymm{}, %xmm{}".format(a_imin1, t1))
            p("vpshufb shuf_5_to_0_zerorest(%rip), %ymm{}, %ymm{}".format(t1, t1))
            p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(0, t1, t1))
            p("vpand coeff_0(%rip), %ymm{}, %ymm{}".format(t1, t1))

    # and now we still need to fix [1] to [15], which we cannot vmovdqu
    t2 = 0
    t3 = 2
    t4 = 3
    p("vmovdqa {}(%rsp), %ymm{}".format(0, t4))
    p("vpsrlq $48, %ymm{}, %ymm{}".format(t4, t2))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), t2, t2))
    p("vpsllq $16, %ymm{}, %ymm{}".format(t4, t3))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t2, t3, t3))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t4, t3, t4))
    p("vpand mask_omit_lowest(%rip), %ymm{}, %ymm{}".format(t4, t4))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t4, t1, t4))
    p("vmovdqa %ymm{}, {}(%rdi)".format(t4, 0))

    p("mov %r8, %rsp")
    p("ret")
