from params import *

p = print

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


def karatsuba_512x512(w, ab, xy, t0, t1, t2, t3, t4, t5, t6):
    """ w: 4 ymm reg. ab: 2 ymm reg. xy: 2 ymm reg. t*: 1 ymm reg """
    a, b = ab[0], ab[1]
    x, y = xy[0], xy[1]

    aPb = t5
    xPy = t6
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a, b, aPb))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, y, xPy))

    aTx = w[0], w[1]
    karatsuba_256x256(aTx, a, x, t0, t1, t2, t3, t4)

    bTy = w[2], w[3]
    karatsuba_256x256(bTy, b, y, t0, t1, t2, t3, t4)

    aPbTxPy = ab
    karatsuba_256x256(aPbTxPy, aPb, xPy, t0, t1, t2, t3, t4)

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aTx[0], aPbTxPy[0], aPbTxPy[0]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aTx[1], aPbTxPy[1], aPbTxPy[1]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bTy[0], aPbTxPy[0], aPbTxPy[0]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(bTy[1], aPbTxPy[1], aPbTxPy[1]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[0], w[1], w[1]))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(aPbTxPy[1], w[2], w[2]))

def store_1024(w, ptr="%rdi"):
    p("vmovdqa %ymm{}, {}({})".format(w[0], 32*0, ptr))
    p("vmovdqa %ymm{}, {}({})".format(w[1], 32*1, ptr))
    p("vmovdqa %ymm{}, {}({})".format(w[2], 32*2, ptr))
    p("vmovdqa %ymm{}, {}({})".format(w[3], 32*3, ptr))

def load_1024(w, ptr="%rdi"):
    p("vmovdqa {}({}), %ymm{}".format(32*0, ptr, w[0]))
    p("vmovdqa {}({}), %ymm{}".format(32*1, ptr, w[1]))
    p("vmovdqa {}({}), %ymm{}".format(32*2, ptr, w[2]))
    p("vmovdqa {}({}), %ymm{}".format(32*3, ptr, w[3]))

def vec256_sr53(r, a, t):
    p("vpand mask1110(%rip), %ymm{}, %ymm{}".format(a, r))
    p("vpsllq ${}, %ymm{}, %ymm{}".format(11, r, r))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00''11''10''01', 2), r, r))
    p("vpsrlq ${}, %ymm{}, %ymm{}".format(53, a, t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, r, r))

def vec256_sl203(r, a, t):
    p("vpand mask0001(%rip), %ymm{}, %ymm{}".format(a, r))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00''11''10''01', 2), r, r))
    p("vpsllq ${}, %ymm{}, %ymm{}".format(11, r, r))

def mul512_and_accumulate(s, r, t):
    # multiply r by x^512, reduce mod x^821-1, add to s
    s1,s2,s3,s4 = s
    t5,t6,t7,t8 = t

    # r[0] is aligned with 512:767
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(r[0], s3, s3))

    # the low 53 of r[1] are aligned with 768:820
    p("vpand low53(%rip), %ymm{}, %ymm{}".format(r[1], t8))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t8, s4, s4))
    # align the high 203 of r[1] with 0:202
    vec256_sr53(t5, r[1], t8)

    # align low 53 of r[2] with 203:255
    vec256_sl203(t6, r[2], t8)
    # align high 203 of r[2] with 256:458
    vec256_sr53(t7, r[2], t8)
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t5, t6, t6))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t6, s1, s1))

    # align low 53 of r[3] with 459:511
    vec256_sl203(t5, r[3], t8)
    # align high 203 of r[3] with 512:714
    vec256_sr53(t6, r[3], t8)
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t5, t7, t7))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t7, s2, s2))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t6, s3, s3))

def mul1024_and_accumulate(s, r, t):
    # multiply r by x^1024 (= x^203), reduce mod x^821 - 1, add to s
    t5,t6,t7 = t

    for i in [0,1,2,3]:
      # s[i] <- s[i] + "high 203 of r[i-1] | low 53 of r[i]"
      vec256_sr53(t5, r[i-1], t7)
      vec256_sl203(t6, r[i], t7)
      p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t5, t6, t6))
      p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t6, s[i], s[i]))

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
    p("mask0001:")
    for i in [65535]*4 + [0]*12:
        p(".word {}".format(i))
    p("mask1110:")
    for i in [0]*4 + [65535]*12:
        p(".word {}".format(i))
    p("low53:")
    for i in [65535]*3 + [31] + [0]*12:
        p(".word {}".format(i))

    p(".text")
    p(".global {}poly_R2_mul".format(NAMESPACE))
    p(".global _{}poly_R2_mul".format(NAMESPACE))

    p("{}poly_R2_mul:".format(NAMESPACE))
    p("_{}poly_R2_mul:".format(NAMESPACE))
    # rdi holds result, rsi holds a, rdx holds b
    # TODO: allow rdi=rsi

    r=0,1,2,3
    a,b=4,5
    w,x=6,7
    t1,t2,t3,t4=8,9,10,11
    t5,t6,t7,t8=12,13,14,15
    p("vmovdqa {}(%rsi), %ymm{}".format( 0, a))
    p("vmovdqa {}(%rsi), %ymm{}".format(32, b))
    p("vmovdqa {}(%rdx), %ymm{}".format( 0, w))
    p("vmovdqa {}(%rdx), %ymm{}".format(32, x))

    karatsuba_512x512(r, (a, b), (w, x), t1, t2, t3, t4, t5, t6, t7)

    # store r mod x^821-1, do not modify r
    vec256_sr53(t1, r[3], t7)
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(r[0], t1, t1))
    p("vpand low53(%rip), %ymm{}, %ymm{}".format(r[3], t2))
    store_1024((t1,r[1],r[2],t2))

    # add r * x^512 mod x^821-1 to output
    s = (a,b,w,x)
    load_1024(s, "%rdi")
    mul512_and_accumulate(s, r, (t1,t2,t3,t4))
    store_1024(s, "%rdi")

    c, d, y, z = 4, 5, 6, 7
    p("vmovdqa {}(%rsi), %ymm{}".format(64, c))
    p("vmovdqa {}(%rsi), %ymm{}".format(96, d))
    p("vmovdqa {}(%rdx), %ymm{}".format(64, y))
    p("vmovdqa {}(%rdx), %ymm{}".format(96, z))

    karatsuba_512x512(r, (c, d), (y, z), t1, t2, t3, t4, t5, t6, t7)

    s = (c,d,y,z)
    load_1024(s, "%rdi")
    mul512_and_accumulate(s, r, (t1,t2,t3,t4))
    mul1024_and_accumulate(s, r, (t1,t2,t3))
    store_1024(s, "%rdi")

    # used all free registers during accumulate, reload inputs
    a,b,w,x=4,5,6,7
    c,d,y,z=8,9,10,11
    t5,t6,t7,t8=12,13,14,15
    load_1024((a,b,c,d), "%rsi")
    load_1024((w,x,y,z), "%rdx")

    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(a, c, a))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(b, d, b))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(w, y, w))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(x, z, x))

    karatsuba_512x512(r, (a,b), (w, x), c, d, y, z, t5, t6, t7)

    # multiply by 512 and reduce mod x^821 - 1
    s = (c,d,y,z)
    load_1024(s, "%rdi")
    mul512_and_accumulate(s, r, (a,b,w,x))
    store_1024(s, "%rdi")

    p("ret")
