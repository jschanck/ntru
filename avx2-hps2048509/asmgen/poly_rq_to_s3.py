
from math import ceil

p = print


def mod3(a, r=13, t=14, c=15):
    # r = (a >> 8) + (a & 0xff); // r mod 255 == a mod 255
    p("vpsrlw $8, %ymm{}, %ymm{}".format(a, r))
    p("vpand mask_ff(%rip), %ymm{}, %ymm{}".format(a, a))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 4) + (r & 0xf); // r' mod 15 == r mod 15
    p("vpand mask_f(%rip), %ymm{}, %ymm{}".format(r, a))
    p("vpsrlw $4, %ymm{}, %ymm{}".format(r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    for _ in range(2):
        p("vpand mask_3(%rip), %ymm{}, %ymm{}".format(r, a))
        p("vpsrlw $2, %ymm{}, %ymm{}".format(r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    #   t = r - 3;
    p("vpsubw mask_3(%rip), %ymm{}, %ymm{}".format(r, t))
    #   c = t >> 15;  t is signed, so shift arithmetic
    p("vpsraw $15, %ymm{}, %ymm{}".format(t, c))

    tmp = a
    #   return (c&r) ^ (~c&t);
    p("vpandn %ymm{}, %ymm{}, %ymm{}".format(t, c, tmp))
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(c, r, t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, tmp, r))


if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")

    p("const_3_repeating:")
    for i in range(16):
        p(".word 0x3")

    p("shuf_b8_to_low_doubleword:")
    for j in range(16):
        p(".byte 8")
        p(".byte 255")

    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")

    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

    p(".text")
    p(".hidden poly_Rq_to_S3")
    p(".global poly_Rq_to_S3")
    p(".att_syntax prefix")

    p("poly_Rq_to_S3:")

    r = 0
    a = 1
    threes = 3
    last = 4
    retval = 5
    p("vmovdqa const_3_repeating(%rip), %ymm{}".format(threes))
    p("vmovdqa {}(%rsi), %ymm{}".format((ceil(509 / 16) - 1)*32, last))

    p("vpsrlw $10, %ymm{}, %ymm{}".format(last, r))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(threes, r, r))
    p("vpsllw $11, %ymm{}, %ymm{}".format(r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, r, last))

    mod3(last, retval)
    p("vpsllw $1, %ymm{}, %ymm{}".format(retval, last))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(last, last))
    p("vpshufb shuf_b8_to_low_doubleword(%rip), %ymm{}, %ymm{}".format(last, last))
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(last, last, last))

    for i in range(ceil(509 / 16)):
        p("vmovdqa {}(%rsi), %ymm{}".format(i*32, a))
        p("vpsrlw $10, %ymm{}, %ymm{}".format(a, r))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(threes, r, r))
        p("vpsllw $11, %ymm{}, %ymm{}".format(r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(a, r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, r, r))
        mod3(r, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, i*32))

    p("ret")
