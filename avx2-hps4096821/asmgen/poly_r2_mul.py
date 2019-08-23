
def mult_128x128(xy, x, y, t1, t2):
    t0 = xy  # careful about pipelining here
    p("vpclmulqdq $1, %xmm{}, %xmm{}, %xmm{}".format(x, y, t0))  # x0 * y1
    p("vpclmulqdq $16, %xmm{}, %xmm{}, %xmm{}".format(x, y, t1))  # x1 * y0
    p("vpclmulqdq $17, %xmm{}, %xmm{}, %xmm{}".format(x, y, t2))  # x1 * y1
    p("vpxor %xmm{}, %xmm{}, %xmm{}".format(t0, t1, t1))
    p("vpclmulqdq $0, %xmm{}, %xmm{}, %xmm{}".format(x, y, t0))  # x0 * y0

    p("vpermq $16, %ymm{}, %ymm{}".format(t1, t1))  # 00 [01 00] 00
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(t2, t2, t2))  # move low of t2 to high

    # TODO can we do this without masks?
    p("vpand mask0011(%rip), %ymm{}, %ymm{}".format(t0, t0))
    p("vpand mask0110(%rip), %ymm{}, %ymm{}".format(t1, t1))
    p("vpand mask1100(%rip), %ymm{}, %ymm{}".format(t2, t2))

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t2, xy))


def karatsuba_256x256(ab, a, b, t0, t1, t2, t3, t4):
    """assumes a and b are two ymm registers"""
    z0, z2 = ab
    a0, a1 = a, t0
    b0, b1 = b, t1
    z1 = t2
    p("vextracti128 $1, %ymm{}, %xmm{}".format(a, a1))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(b, b1))
    mult_128x128(z2, a1, b1, t3, t4)

    p("vpxor %xmm{}, %xmm{}, %xmm{}".format(a0, a1, a1))  # a1 contains [0][a0 xor a1]
    p("vpxor %xmm{}, %xmm{}, %xmm{}".format(b0, b1, b1))
    mult_128x128(z1, a1, b1, t3, t4)
    mult_128x128(z0, a0, b0, t3, t4)

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z1, z2, z1))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z1, z0, z1))

    # put top half of z1 into t (contains [0][z1top])
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, t0, t0))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(z1, t0))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z2, t0, z2))  # compose into z2

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, t0, t0))
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(z1, t0, t0))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, z0, z0))
    # ~512bit result is now in z2 and z0


def karatsuba_256x256_destroy_a(ab, a, b, t0, t1, t2, t3):
    """assumes a and b are two ymm registers"""
    z0, z2 = ab
    a0, a1 = a, t0
    b0, b1 = b, t1
    p("vextracti128 $1, %ymm{}, %xmm{}".format(a, a1))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(b, b1))
    mult_128x128(z2, a1, b1, t2, t3)

    mult_128x128(z0, a0, b0, t2, t3)
    z1 = t2
    p("vpxor %xmm{}, %xmm{}, %xmm{}".format(a0, a1, a1))  # a1 contains [0][a0 xor a1]
    p("vpxor %xmm{}, %xmm{}, %xmm{}".format(b0, b1, b1))
    mult_128x128(z1, a1, b1, a0, b0)

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z1, z2, z1))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z1, z0, z1))

    # put top half of z1 into t (contains [0][z1top])
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, t0, t0))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(z1, t0))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(z2, t0, z2))  # compose into z2

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, t0, t0))
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(z1, t0, t0))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t0, z0, z0))
    # ~512bit result is now in z2 and z0


p = print

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")
    p("mask1100:")
    for i in [0]*8 + [65535]*8:
        p(".word {}".format(i))
    p("mask0110:")
    for i in [0]*4 + [65535]*8 + [0]*4:
        p(".word {}".format(i))
    p("mask0011:")
    for i in [65535]*8 + [0]*8:
        p(".word {}".format(i))
    p("mask1000:")
    for i in [0]*12 + [65535]*4:
        p(".word {}".format(i))
    p("mask0111:")
    for i in [65535]*12 + [0]*4:
        p(".word {}".format(i))
    p("low165:")
    for i in [65535]*10 + [31] + [0]*4:
        p(".word {}".format(i))

    p(".text")
    p(".hidden poly_R2_mul")
    p(".global poly_R2_mul")
    p(".att_syntax prefix")

    p("poly_R2_mul:")

    a, x = 0, 3
    b, y = 1, 4
    # c, z = 2, 5  # we do not need these yet
    p("vmovdqa {}(%rsi), %ymm{}".format(0, a)) # load a
    p("vmovdqa {}(%rsi), %ymm{}".format(32, b)) # load b
    p("vmovdqa {}(%rdx), %ymm{}".format(0, x)) # load x
    p("vmovdqa {}(%rdx), %ymm{}".format(32, y)) # load y

    aPb = 6
    xPy = 7

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a, b, aPb))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, y, xPy))

    t0, t1, t2, t3, t4 = (11, 12, 13, 14, 15)

    w0 = aTx = 2, 5
    karatsuba_256x256(aTx, a, x, t0, t1, t2, t3, t4)
    # finished w0
    # free: 8, 9, 10, a, x

    aPbTxPy = 8, 9
    karatsuba_256x256(aPbTxPy, aPb, xPy, t0, t1, t2, t3, t4)
    # free: 10, a, x
    w2 = aPbTxPy

    w1 = a, x
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[0], aTx[0], w1[0]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[1], aTx[1], w1[1]))
    # by already merging w0[1], we do not need to store it and recompose later
    # the same goes for w1[1]. This frees up registers!
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(w0[1], w1[0], w1[0]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(w1[1], w2[0], w2[0]))

    c, z = 10, t4
    p("vmovdqa {}(%rsi), %ymm{}".format(64, c)) # load c
    p("vmovdqa {}(%rdx), %ymm{}".format(64, z)) # load z

    aPbPc = aPb
    xPyPz = xPy
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPb, c, aPbPc))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(xPy, z, xPyPz))

    aPbPcTxPyPz = w1[1], w0[1]
    karatsuba_256x256_destroy_a(aPbPcTxPyPz, aPbPc, xPyPz, t0, t1, t2, t3)

    for i in range(2):
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbPcTxPyPz[i], w2[i], w2[i]))
    # free: aPbPc, xPyPz, aPbPcTxPyPz[0, 1]

    bPc = aPbPc
    yPz = xPyPz
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(b, c, bPc))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(y, z, yPz))

    bPcTyPz = aPbPcTxPyPz
    karatsuba_256x256_destroy_a(bPcTyPz, bPc, yPz, t0, t1, t2, t3)

    for i in range(2):
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bPcTyPz[i], w2[i], w2[i]))
    # finished w2
    # free: bPc, yPz

    bTy = bPc, yPz
    karatsuba_256x256_destroy_a(bTy, b, y, t0, t1, t2, t3)
    # free b, y

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bTy[0], w1[0], w1[0]))
    # this is actually part of w1, but we have already merged w1[1] into w2[0]
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bTy[1], w2[0], w2[0]))
    # finished w1

    w3 = bPcTyPz
    for i in range(2):
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bTy[i], w3[i], w3[i]))
    # free bTy[0, 1], b, y

    cTz = b, y
    karatsuba_256x256_destroy_a(cTz, c, z, t0, t1, t2, t3)
    # free bTy[0, 1], c, z (c=10, z=t4)
    w4 = cTz
    # finished w4

    for i in range(2):
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(cTz[i], w3[i], w3[i]))
    # finished w3

    # recompose w2[1] into w3 and w3 into w4
    # note that w0 -> w1 and w1 -> w2 has already been done to save registers
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(w2[1], w3[0], w3[0]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(w3[1], w4[0], w4[0]))
    # free bTy[0, 1], w2[1], w3[1], 10

    w = w0, w1, w2, w3, w4, w5 = w0[0], w1[0], w2[0], w3[0], w4[0], w4[1]

    for i, word in enumerate(w[:3]):
        p("vpand mask1100(%rip), %ymm{}, %ymm{}".format(w[i+2], t2))
        p("vpand mask0011(%rip), %ymm{}, %ymm{}".format(w[i+3], t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t2, t1))

        p("vpsrlq ${}, %ymm{}, %ymm{}".format(37, t1, t1))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('01' '00' '11' '10', 2), t1, t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, w[i], w[i]))

        p("vpand mask1000(%rip), %ymm{}, %ymm{}".format(w[i+2], t1))
        p("vpand mask0111(%rip), %ymm{}, %ymm{}".format(w[i+3], t2))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t2, t1))

        p("vpsllq ${}, %ymm{}, %ymm{}".format(27, t1, t1))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('10' '01' '00' '11', 2), t1, t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, w[i], w[i]))

    p("vpand low165(%rip), %ymm{}, %ymm{}".format(w2, w2))

    p("vmovdqa %ymm{}, {}(%rdi)".format(w0, 0))
    p("vmovdqa %ymm{}, {}(%rdi)".format(w1, 32))
    p("vmovdqa %ymm{}, {}(%rdi)".format(w2, 64))

    p("ret")
