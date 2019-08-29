p = print

from params import *
from mod3 import mod3, mod3_masks
from math import ceil

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")

    p("cast8_to_16:")
    for i in range(8):
      p(".byte 255")
      p(".byte {}".format(i))
    for i in range(8):
      p(".byte 255")
      p(".byte {}".format(i))

    mod3_masks()

    p(".text")
    p(".hidden sample_iid")
    p(".global sample_iid")
    p(".att_syntax prefix")

    p("sample_iid:")
    # rdi holds r
    # rsi holds uniformbytes

    t = 1
    retval = 2
    b = 3
    for i in range(NTRU_N32//32):
        p("vmovdqu {}(%rsi), %ymm{}".format(i*32, b))
        p("vextracti128 $0, %ymm{}, %xmm{}".format(b, t))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('11' '01' '10' '00', 2), t, t))
        p("vpshufb cast8_to_16(%rip), %ymm{}, %ymm{}".format(t,t))
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, (2*i)*32))

        p("vextracti128 $1, %ymm{}, %xmm{}".format(b, t))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('11' '01' '10' '00', 2), t, t))
        p("vpshufb cast8_to_16(%rip), %ymm{}, %ymm{}".format(t,t))
        # shuffle
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, (2*i+1)*32))

    for i in range(NTRU_N-1, NTRU_N32):
      p("movw $0, {}(%rdi)".format(2*i))
    p("ret")
