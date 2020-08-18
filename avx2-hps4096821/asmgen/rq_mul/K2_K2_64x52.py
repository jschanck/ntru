
from schoolbook_64x13 import schoolbook_64x13 as mul_64x13
from transpose import transpose_64x16_to_16x52, transpose_16x128_to_128x16
import random

p = print

SALT = 0

def K2_K2_transpose_64x52(r_real='%rdi', a_real='%rsi', b_real='%rdx', coeffs=52, transpose=True):
    """ coeffs should be set to 64 if polynomials are allocated like that"""
    # allocate space for;
    # - (A[0:13]+B[0:13])*(C[0:13]+D[0:13]) inside K2-step
    # - (a[0:26] + a[26:52]) before 3rd K2-step
    # - (b[0:26] + b[26:52]) before 3rd K2-step
    # - output of third 26x26 multiplication

    global SALT
    SALT += 1

    p("subq ${}, %rsp".format((52 + 52 + 128 + 26 + 26 + 26 + 52) * 32))
    a_transpose = 0
    b_transpose = a_transpose + 52
    r_transpose = b_transpose + 52
    a_b_summed = r_transpose + 128
    a_in_rsp = a_b_summed + 26
    b_in_rsp = a_in_rsp + 26
    t2_in_rsp = b_in_rsp + 26

    t0 = 0
    t1 = 1
    p("mov $4, %ecx")
    p("karatsuba_loop_{}:".format(SALT))

    if transpose:
        a_off = a_transpose
        b_off = b_transpose
        r_off = r_transpose
        # support multiple calling conventions without wasting registers
        # - cannot use rsp, since incrementing it messes up other stack values
        # - use the same for a_mem and b_mem, but not for r_mem;
        #    since r_mem is incremented twice as fast
        p("mov %rsp, %r9")
        a_mem = b_mem = '%r9'
        p("mov %rsp, %r10")
        r_mem = '%r10'
        transpose_64x16_to_16x52(dst=a_mem, src=a_real, dst_off=a_off)
        transpose_64x16_to_16x52(dst=b_mem, src=b_real, dst_off=b_off)
        coeffs = 64  # this is needed if input/output is aligned on 16 words
    else:
        a_off = b_off = r_off = 0
        a_mem = a_real
        b_mem = b_real
        r_mem = r_real

    # Outer karatsuba low26 * low26 and high26 * high26
    # First pass through innerloop does low * low, second does high * high
    p("innerloop_{}:".format(SALT))

    mul_64x13(r_mem, a_mem, b_mem, r_off, a_off, b_off)
    mul_64x13(r_mem, a_mem, b_mem, r_off+26, a_off+13, b_off+13)
    mul_64x13('%rsp', a_mem, b_mem, a_b_summed, a_off, b_off, additive=True)

    # r->coeffs[25] = t2.coeffs[12] - r->coeffs[12] - r->coeffs[38];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(12+a_b_summed), t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(12+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(38+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(25+r_off), r_mem))

    for i in range(12):
        # r->coeffs[13 + i] -= r->coeffs[26 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(13+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(26+i+r_off), r_mem, t0, t0))

        # r->coeffs[26 + i] = t2.coeffs[13 + i] - r->coeffs[13 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(13+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[26 + i] -= r->coeffs[39 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(39+i+r_off), r_mem, t1, t1))

        # r->coeffs[13 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[13 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(13+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(26+i+r_off), r_mem))

    p("neg %ecx")  # abuse ecx as toggle so we can do the above loop twice
    p("jns done_{}".format(SALT))
    p("add ${}, {}".format(32 * 26, a_mem))
    if a_mem != b_mem:  # we would not want to modify the same pointer twice
        p("add ${}, {}".format(32 * 26, b_mem))
    p("add ${}, {}".format(32 * 52, r_mem))
    p("jmp innerloop_{}".format(SALT))
    p("done_{}:".format(SALT))  # this label is used so we do not do unnecessary additions on the last loop

    p("sub ${}, {}".format(32 * 26, a_mem))
    if a_mem != b_mem:
        p("sub ${}, {}".format(32 * 26, b_mem))
    p("sub ${}, {}".format(32 * 52, r_mem))

    # Outer karatsuba (l26+h26) * (l26+h26)
    # store half-limb sums on stack
    for i in range(26):
        p("vmovdqa {}({}), %ymm{}".format(32*(i+a_off), a_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(26 + i + a_off), a_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(a_in_rsp + i)))

        p("vmovdqa {}({}), %ymm{}".format(32*(i+b_off), b_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(26 + i+b_off), b_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(b_in_rsp + i)))

    mul_64x13('%rsp', '%rsp', '%rsp', t2_in_rsp, a_in_rsp, b_in_rsp)
    mul_64x13('%rsp', '%rsp', '%rsp', t2_in_rsp + 26, a_in_rsp + 13, b_in_rsp + 13)
    mul_64x13('%rsp', '%rsp', '%rsp', a_b_summed, a_in_rsp, b_in_rsp, additive=True)

    for i in range(12):
        # t2b.coeffs[13 + i] -= t2b.coeffs[26 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+13+i), t0))
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+26+i), t0, t0))

        # t2b.coeffs[26 + i] = t2.coeffs[13 + i] - t2b.coeffs[13 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(13+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # t2b.coeffs[26 + i] -= t2b.coeffs[39 + i];
        # store t2b.coeffs[26 + i] in a register for later use during recomposition
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+39+i), t1, 4+i))

        # t2b.coeffs[13 + i] -= t2b.coeffs[i];
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + i), t0, t0))

        # t2b.coeffs[13 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(t2_in_rsp+13+i)))

    # t2b.coeffs[25] = t2.coeffs[12] - t2b.coeffs[12] - t2b.coeffs[38];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(12+a_b_summed), t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 12), t0, t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 38), t0, t0))

    # compose outer Karatsuba (t2b.coeffs[25] is still in t0)
    # r->coeffs[51] = t2b.coeffs[25] - r->coeffs[25] - r->coeffs[77];
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(25+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(77+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(51+r_off), r_mem))

    for i in range(25):
        # r->coeffs[26 + i] -= r->coeffs[52 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(26+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(52+i+r_off), r_mem, t0, t0))

        # r->coeffs[52 + i] = t2b.coeffs[26 + i] - r->coeffs[26 + i];
        if i < 12:  # we still have a few stored in registers
            t1 = 4+i
        else:
            t1 = 1
            p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+26+i), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[52 + i] -= r->coeffs[78 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(78+i+r_off), r_mem, t1, t1))

        # r->coeffs[26 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[26 + i] += t2b.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+i), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(26+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(52+i+r_off), r_mem))

    # explicitly zero out the 103rd coefficient, as this makes it much nicer
    # to deal with these results in a vectorized way when interpolating.
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t1, t1))
    p("vmovdqa %ymm{}, {}({})".format(t1, 32*(103+r_off), r_mem))

    if transpose:
        transpose_16x128_to_128x16(dst=r_real, src=r_mem, src_off=r_transpose)

    p("add ${}, {}".format(2*16 * coeffs, a_real))
    p("add ${}, {}".format(2*16 * coeffs, b_real))
    p("add ${}, {}".format(2*16 * coeffs*2, r_real))
    p("dec %ecx")
    p("jnz karatsuba_loop_{}".format(SALT))
    # restore the original value of r_real to prevent caller confusion
    p("sub ${}, {}".format(4 * (2*16 * coeffs*2), r_real))
    p("add ${}, %rsp".format((52 + 52 + 128 + 26 + 26 + 26 + 52) * 32))

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".p2align 5")

    p(".text")
    p(".global K2_K2_schoolbook_64x52coef")
    p(".global K2_K2_schoolbook_64x52coef_transpose")
    p(".att_syntax prefix")

    p("K2_K2_schoolbook_64x52coef:")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    K2_K2_transpose_64x52(transpose=False)

    p("mov %r8, %rsp")
    p("ret")

    p("K2_K2_schoolbook_64x52coef_transpose:")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    K2_K2_transpose_64x52()

    p("mov %r8, %rsp")
    p("ret")
