from math import ceil

p = print


if __name__ == '__main__':
    p(".data")
    p(".align 32")

    p("lookup_L:")
    for i in range(8):
        p(".word 0x2118")
        p(".word 0x0006")

    p("fives:")
    for i in range(16):
        p(".word 0x5555")

    p("threes_32:")
    for i in range(8):
        p(".word 0x3")
        p(".word 0x0")

    p("threes_32_b:")
    for i in range(8):
        p(".word 0x6")  # 0x3 << 1
        p(".word 0x0")

    p("a_shifts:")
    for i in range(8):
        p(".word {}".format(i * 4))
        p(".word 0x0")

    p("b_shifts:")
    for i in range(8):
        p(".word {}".format(i * 4 + 2 - 1))  # -1 to compensate for later shl
        p(".word 0x0")

    p(".text")
    p(".global cbdS3")
    p(".att_syntax prefix")

    p("cbdS3:")

    t0 = 7
    t = 0
    d = 1
    a = 2
    b = 3
    L = 4
    L2 = 5
    dst = 6

    threes_32 = 8
    threes_32_b = 9
    fives = 10
    a_shifts = 11
    b_shifts = 12

    p("vmovdqa a_shifts, %ymm{}".format(a_shifts))
    p("vmovdqa b_shifts, %ymm{}".format(b_shifts))
    p("vmovdqa lookup_L, %ymm{}".format(L))
    p("vmovdqa threes_32, %ymm{}".format(threes_32))
    p("vmovdqa threes_32_b, %ymm{}".format(threes_32_b))
    p("vmovdqa fives, %ymm{}".format(fives))

    for i in range(ceil(701 / 8)):
        if i % 4 == 0:
            p("vmovdqa {}(%rsi), %xmm{}".format((i // 2)*8, t0))
        else:
            p("vpshufd ${}, %ymm{}, %ymm{}".format(int('00111001', 2), t0, t0))
        p("vbroadcastss %xmm{}, %ymm{}".format(t0, t))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(fives, t, d))
        p("vpsrld $1, %ymm{}, %ymm{}".format(t, t))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(fives, t, t))
        p("vpaddd %ymm{}, %ymm{}, %ymm{}".format(t, d, d))

        p("vpsrlvd %ymm{}, %ymm{}, %ymm{}".format(a_shifts, d, a))
        p("vpsrlvd %ymm{}, %ymm{}, %ymm{}".format(b_shifts, d, b))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(threes_32, a, a))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(threes_32_b, b, b))
        p("vpslld $3, %ymm{}, %ymm{}".format(a, a))
        # no need to shift b, as we embed this in the vpsrlvd

        # apply lookup L based on a and b
        p("vpsrlvd %ymm{}, %ymm{}, %ymm{}".format(a, L, L2))
        p("vpsrlvd %ymm{}, %ymm{}, %ymm{}".format(b, L2, L2))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(threes_32, L2, L2))

        # convert doublewords into words
        p("vpackusdw %ymm{}, %ymm{}, %ymm{}".format(L2, L2, L2))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('11011000', 2), L2, dst))

        if i*16 + 32 <= 704 * 2:
            p("vmovdqu %ymm{}, {}(%rdi)".format(dst, i*16))
        else:
            p("vmovq %xmm{}, {}(%rdi)".format(dst, i*16))
            p("movq $0, {}(%rdi)".format(i*16+8))  # cap at degree N-1

    p("ret")
