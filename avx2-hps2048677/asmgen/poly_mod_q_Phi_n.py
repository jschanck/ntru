
p = print

from params import *

if __name__ == '__main__':
    p(".data")
    p(".p2align 5")

    p(".text")
    p(".global {}poly_mod_q_Phi_n".format(NAMESPACE))
    p(".global _{}poly_mod_q_Phi_n".format(NAMESPACE))

    p("{}poly_mod_q_Phi_n:".format(NAMESPACE))
    p("_{}poly_mod_q_Phi_n:".format(NAMESPACE))
    # rdi holds r

    N_min_1 = 0
    t = 1
    # NTRU_N is in 677th element;  5th word of 43th register
    p("vmovdqa {}(%rdi), %ymm{}".format(42*32, N_min_1))
    p("vpermq ${}, %ymm{}, %ymm{}".format(int('00' '00' '00' '01', 2), N_min_1, N_min_1))
    # move into high 16 in doubleword (to clear high 16)
    p("vpslld $16, %ymm{}, %ymm{}".format(N_min_1, N_min_1))
    # clone into bottom 16
    p("vpsrld $16, %ymm{}, %ymm{}".format(N_min_1, t))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(N_min_1, t, N_min_1))
    # and now it's everywhere in N_min_1
    p("vbroadcastss %xmm{}, %ymm{}".format(N_min_1, N_min_1))
    # negate it
    p("vxorpd %ymm{}, %ymm{}, %ymm{}".format(t,t,t))
    p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(N_min_1, t, N_min_1))

    for i in range(NTRU_N32//16):
        p("vpaddw {}(%rdi), %ymm{}, %ymm{}".format(i*32, N_min_1, t))
        p("vmovdqa %ymm{}, {}(%rdi)".format(t, i*32))

    p("ret")
