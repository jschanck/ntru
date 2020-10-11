p = print

from params import *
from mod3 import mod3, mod3_masks

LOGQ = 0
while 2**LOGQ < NTRU_Q: LOGQ +=1

if __name__ == '__main__':
    p(".data")
    p(".p2align 5")

    p("mask_modq:")
    for i in range(16):
        p(".word {}".format(NTRU_Q-1))

    p("const_half_q_minus_1:")
    for i in range(16):
        p(".word {}".format(NTRU_Q//2-1))

    mod3_masks()

    p(".text")
    p(".global {}poly_Rq_to_S3".format(NAMESPACE))
    p(".global _{}poly_Rq_to_S3".format(NAMESPACE))

    p("{}poly_Rq_to_S3:".format(NAMESPACE))
    p("_{}poly_Rq_to_S3:".format(NAMESPACE))

    a = 0
    flag = 1
    r = 2
    last = 4
    const_half_q_minus_1 = 5
    modq = 6

    p("vmovdqa mask_modq(%rip), %ymm{}".format(modq))
    p("vmovdqa const_half_q_minus_1(%rip), %ymm{}".format(const_half_q_minus_1))

    p("vmovdqa {}(%rsi), %ymm{}".format(2*(16*((NTRU_N-1) // 16)), last))

    # broadcast last coefficient to all 16 words
    quadword_of_last = ((NTRU_N-1)%16)//4
    if quadword_of_last != 0:
        p("vpermq ${}, %ymm{}, %ymm{}".format(quadword_of_last, last, last))
    word_of_low = (NTRU_N-1)%4
    if word_of_low != 0:
        p("vpsrlq ${}, %ymm{}, %ymm{}".format(16*word_of_low, last, last))
    p("vpslld $16, %ymm{}, %ymm{}".format(last, r))
    p("vpsrld $16, %ymm{}, %ymm{}".format(r, last))
    p("vpor %ymm{}, %ymm{}, %ymm{}".format(last, r, last))
    p("vbroadcastss %xmm{}, %ymm{}".format(last, last))

    # Add (-q) mod 3 to last if last is > q/2.
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(modq, last, last));
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, const_half_q_minus_1, flag))
    p("vpsrlw ${}, %ymm{}, %ymm{}".format(LOGQ, flag, flag))
    if LOGQ%2==0:
        p("vpsllw ${}, %ymm{}, %ymm{}".format(1, flag, flag))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, flag, last))

    mod3(last, r)
    # Multiply last by 2 since we want to subtract its value mod 3.
    p("vpsllw $1, %ymm{}, %ymm{}".format(r, last))

    for i in range(NTRU_N32 // 16):
        p("vmovdqa {}(%rsi), %ymm{}".format(i*32, a))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(modq, a, a));

        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(a, const_half_q_minus_1, flag))
        p("vpsrlw ${}, %ymm{}, %ymm{}".format(LOGQ, flag, flag))
        if LOGQ%2==0:
            p("vpsllw ${}, %ymm{}, %ymm{}".format(1, flag, flag))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(a, flag, a))

        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(a, last, a))
        mod3(a, r)
        p("vmovdqa %ymm{}, {}(%rdi)".format(r, i*32))

    p("ret")
