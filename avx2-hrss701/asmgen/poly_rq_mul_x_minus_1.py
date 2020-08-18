from math import ceil

from params import *

p = print


if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".p2align 5")

    p("mask_mod8192:")
    for i in range(16):
        p(".word 8191")

    p("mask_mod8192_omit_lowest:")
    p(".word 0")
    for i in range(15):
        p(".word 8191")

    p("mask_mod8192_only_lowest:")
    p(".word 8191")
    for i in range(15):
        p(".word 0")

    p("shuf_5_to_0_zerorest:")
    for i in range(2):
        p(".byte {}".format((i + 2*5) % 16))
    for i in range(30):
        p(".byte 255")

    p(".text")
    p(".global {}poly_Rq_mul_x_minus_1".format(NAMESPACE))
    p(".att_syntax prefix")

    p("{}poly_Rq_mul_x_minus_1:".format(NAMESPACE))

    a_imin1 = 0
    t0 = 1
    t1 = 4
    for i in range(ceil(701 / 16)-1, 0, -1):
        p("vmovdqu {}(%rsi), %ymm{}".format((i*16 - 1) * 2, a_imin1))
        p("vpsubw {}(%rsi), %ymm{}, %ymm{}".format(i * 32, a_imin1, t0))
        p("vpand mask_mod8192(%rip), %ymm{}, %ymm{}".format(t0, t0))
        p("vmovdqa %ymm{}, {}(%rdi)".format(t0, i*32))
        if i == ceil(701 / 16)-1:
            # a_imin1 now contains 687 to 702 inclusive;
            # we need 700 for [0], which is at position 14
            p("vextracti128 $1, %ymm{}, %xmm{}".format(a_imin1, t1))
            p("vpshufb shuf_5_to_0_zerorest(%rip), %ymm{}, %ymm{}".format(t1, t1))
            p("vpsubw {}(%rsi), %ymm{}, %ymm{}".format(0, t1, t1))
            p("vpand mask_mod8192_only_lowest(%rip), %ymm{}, %ymm{}".format(t1, t1))

    # and now we still need to fix [1] to [15], which we cannot vmovdqu
    t2 = 0
    t3 = 2
    t4 = 3
    p("vmovdqa {}(%rsi), %ymm{}".format(0, t4))
    p("vpsrlq $48, %ymm{}, %ymm{}".format(t4, t2))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), t2, t2))
    p("vpsllq $16, %ymm{}, %ymm{}".format(t4, t3))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t2, t3, t3))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t4, t3, t4))
    p("vpand mask_mod8192_omit_lowest(%rip), %ymm{}, %ymm{}".format(t4, t4))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t4, t1, t4))
    p("vmovdqa %ymm{}, {}(%rdi)".format(t4, 0))

    p("ret")
