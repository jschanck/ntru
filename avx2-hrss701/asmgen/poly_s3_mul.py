
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


from math import ceil


if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
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

    p(".text")
    p(".hidden poly_S3_mul")
    p(".global poly_S3_mul")
    p(".att_syntax prefix")

    p("poly_S3_mul:")
    p("call poly_Rq_mul")
    # result pointer *r is still in %rdi

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

    p("ret")
