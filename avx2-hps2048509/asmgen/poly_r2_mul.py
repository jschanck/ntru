from params import *

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


p = print

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".p2align 5")
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
    p("low253:")
    for i in [65535]*15 + [8191]:
        p(".word {}".format(i))

    p(".text")
    p(".global {}poly_R2_mul".format(NAMESPACE))
    p(".global _{}poly_R2_mul".format(NAMESPACE))

    p("{}poly_R2_mul:".format(NAMESPACE))
    p("_{}poly_R2_mul:".format(NAMESPACE))

    # Since we have the vpclmulqdq instruction to multiply 64-bit polynomials over GF(2^k)
    # we try to reduce our computation to multiplications of 64-bit polynomials. In this implementation
    # this is done by two instances of karatsuba followed by one schoolbook multiplication (which is computed using vpclmulqdq).
    # This results in 36 (3*3*4) multiplications of 64-bit polynomials. There are no intermediate loads/stores.
    a, x = 0, 3
    b, y = 1, 4
    p("vmovdqa {}(%rsi), %ymm{}".format(0, a)) # load a
    p("vmovdqa {}(%rsi), %ymm{}".format(32, b)) # load b
    p("vmovdqa {}(%rdx), %ymm{}".format(0, x)) # load x
    p("vmovdqa {}(%rdx), %ymm{}".format(32, y)) # load y

    aPb = 6
    xPy = 7
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a, b, aPb))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, y, xPy))

    # some temporary registers which we can freely use for multiplication
    t0, t1, t2, t3, t4 = (11, 12, 13, 14, 15)

    w0 = aTx = 2, 5
    karatsuba_256x256(aTx, a, x, t0, t1, t2, t3, t4)
    # finished w0
    # free: 8, 9, 10, a, x

    w1 = bTy = 8, 9
    karatsuba_256x256(bTy, b, y, t0, t1, t2, t3, t4)
    # finished w1
    # free: 10, a, b, x, y

    aPbTxPy = a, b
    karatsuba_256x256(aPbTxPy, aPb, xPy, t0, t1, t2, t3, t4)
    # free: 6, 7, 10, x, y

    # Constructing the 1024-bit polynomial. Note that both addition and subtraction are simply xor when working mod 2.
    for i in range(2):
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[i], w0[i], aPbTxPy[i]))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[i], w1[i], aPbTxPy[i]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[0], w0[1], w0[1]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[1], w1[0], w1[0]))

    w = w0, w1, w2, w3 = w0[0], w0[1], w1[0], w1[1]

    # Reduce from 1024-bit polynomial to 509 coefficient polynomial. The shifts are necessary to make sure the reduction
    # accounts for the fact that the polynomial only has 509 coefficients and not 512.
    # (So x^509 instead of x^512 needs to be added to x^0)
    for i, word in enumerate(w[:2]):
        p("vpand mask1000(%rip), %ymm{}, %ymm{}".format(w[i+1], t2))
        p("vpand mask0111(%rip), %ymm{}, %ymm{}".format(w[i+2], t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t2, t1))

        p("vpsrlq ${}, %ymm{}, %ymm{}".format(61, t1, t1))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('10010011', 2), t1, t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, w[i], w[i]))

        p("vpsllq ${}, %ymm{}, %ymm{}".format(3, w[i+2], t1))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, w[i], w[i]))

    # Get rid of the last three bits (509 coefficients and not 512)
    p("vpand low253(%rip), %ymm{}, %ymm{}".format(w1, w1))

    p("vmovdqa %ymm{}, {}(%rdi)".format(w0, 0))
    p("vmovdqa %ymm{}, {}(%rdi)".format(w1, 32))

    p("ret")
