p = print

from params import *
from mod3 import mod3, mod3_masks
from math import ceil

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")

    mod3_masks()

    p(".text")
    p(".hidden poly_mod_3_Phi_n")
    p(".global poly_mod_3_Phi_n")
    p(".att_syntax prefix")

    p("poly_mod_3_Phi_n:")
    # rdi holds r

    N_min_1 = 0
    t = 1
    # NTRU_N is in 677th element;  5th word of 43th register
    p("vmovdqa {}(%rdi), %ymm{}".format(42*32, N_min_1))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00' '00' '00' '01', 2), N_min_1, N_min_1))
    # move into high 16 in doubleword (to clear high 16) and multiply by two
    p("vpslld $17, %ymm{}, %ymm{}".format(N_min_1, N_min_1))
    # clone into bottom 16
    p("vpsrld $16, %ymm{}, %ymm{}".format(N_min_1, t))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(N_min_1, t, N_min_1))
    # and now it's everywhere in N_min_1
    p("vbroadcastss %xmm{}, %ymm{}".format(N_min_1, N_min_1))

    retval = 2
    for i in range(NTRU_N32//16):
        p("vpaddw {}(%rdi), %ymm{}, %ymm{}".format(i*32, N_min_1, t))
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, i*32))

    for i in range(NTRU_N, NTRU_N32):
      p("movw $0, {}(%rdi)".format(2*i))
    p("ret")
