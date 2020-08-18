p = print

from params import *
from mod3 import mod3, mod3_masks

LOGQ = 0
while 2**LOGQ < NTRU_Q: LOGQ +=1

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".p2align 5")

    p("const_3_repeating:")
    for i in range(16):
        p(".word 0x3")

    p("shuf_b8_to_low_doubleword:")
    for j in range(16):
        p(".byte 8")
        p(".byte 255")

    p("mask_modq:")
    for i in range(16):
        p(".word {}".format(NTRU_Q-1))

    mod3_masks()

    p(".text")
    p(".hidden {}poly_Rq_to_S3".format(NAMESPACE))
    p(".global {}poly_Rq_to_S3".format(NAMESPACE))
    p(".att_syntax prefix")

    p("{}poly_Rq_to_S3:".format(NAMESPACE))

    r = 0
    a = 1
    threes = 3
    last = 4
    retval = 5
    modq = 6
    p("vmovdqa const_3_repeating(%rip), %ymm{}".format(threes))
    p("vmovdqa mask_modq(%rip), %ymm{}".format(modq))
    p("vmovdqa {}(%rsi), %ymm{}".format((NTRU_N32 // 16 - 1)*32, last))
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(modq, last, last));

    p("vpsrlw ${}, %ymm{}, %ymm{}".format(LOGQ-1, last, r))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(threes, r, r))
    p("vpsllw ${}, %ymm{}, %ymm{}".format(LOGQ, r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, r, last))

    mod3(last, retval)
    p("vpsllw $1, %ymm{}, %ymm{}".format(retval, last))
    p("vextracti128 $1, %ymm{}, %xmm{}".format(last, last))
    p("vpshufb shuf_b8_to_low_doubleword(%rip), %ymm{}, %ymm{}".format(last, last))
    p("vinserti128 $1, %xmm{}, %ymm{}, %ymm{}".format(last, last, last))

    for i in range(NTRU_N32 // 16):
        p("vmovdqa {}(%rsi), %ymm{}".format(i*32, a))
        p("vpand %ymm{}, %ymm{}, %ymm{}".format(modq, a, a));
        p("vpsrlw ${}, %ymm{}, %ymm{}".format(LOGQ-1, a, r))
        p("vpxor %ymm{}, %ymm{}, %ymm{}".format(threes, r, r))
        p("vpsllw ${}, %ymm{}, %ymm{}".format(LOGQ, r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(a, r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(last, r, r))
        mod3(r, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, i*32))

    p("ret")
