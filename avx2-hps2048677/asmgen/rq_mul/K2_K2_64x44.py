
from K2_schoolbook_64x11 import K2_schoolbook_64x11 as mul_64x11
from transpose import transpose_48x16_to_16x44, transpose_16x96_to_96x16
import random

p = print


def K2_K2_transpose_64x44(r_real='%rdi', a_real='%rsi', b_real='%rdx', coeffs=44, transpose=True):
    """ coeffs should be set to 48 if polynomials are allocated like that"""
    # allocate space for;
    # - (A[0:11]+B[0:11])*(C[0:11]+D[0:11]) inside K2-step
    # - (a[0:22] + a[22:44]) before 3rd K2-step
    # - (b[0:22] + b[22:44]) before 3rd K2-step
    # - output of third 22x22 multiplication

    SALT = '{:16x}'.format(random.randint(0, 2**128))  # prevent duplicate labels

    p("subq ${}, %rsp".format((44 + 44 + 96 + 22 + 22 + 22 + 44) * 32))
    a_transpose = 0
    b_transpose = a_transpose + 44
    r_transpose = b_transpose + 44
    a_b_summed = r_transpose + 96
    a_in_rsp = a_b_summed + 22
    b_in_rsp = a_in_rsp + 22
    t2_in_rsp = b_in_rsp + 22

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
        transpose_48x16_to_16x44(dst=a_mem, src=a_real, dst_off=a_off)
        transpose_48x16_to_16x44(dst=b_mem, src=b_real, dst_off=b_off)
        coeffs = 48  # this is needed if input/output is aligned on 16 words
    else:
        a_off = b_off = r_off = 0
        a_mem = a_real
        b_mem = b_real
        r_mem = r_real

    p("innerloop_{}:".format(SALT))

    mul_64x11(r_mem, a_mem, b_mem, r_off, a_off, b_off)
    mul_64x11(r_mem, a_mem, b_mem, r_off+22, a_off+11, b_off+11)
    mul_64x11('%rsp', a_mem, b_mem, a_b_summed, a_off, b_off, additive=True)

    # r->coeffs[21] = t2.coeffs[10] - r->coeffs[10] - r->coeffs[32];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(10+a_b_summed), t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(10+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(32+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(21+r_off), r_mem))

    for i in range(10):
        # r->coeffs[11 + i] -= r->coeffs[22 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(11+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(22+i+r_off), r_mem, t0, t0))

        # r->coeffs[22 + i] = t2.coeffs[11 + i] - r->coeffs[11 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(11+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[22 + i] -= r->coeffs[33 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(33+i+r_off), r_mem, t1, t1))

        # r->coeffs[11 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[11 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(11+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(22+i+r_off), r_mem))

    p("neg %ecx")  # abuse ecx as toggle so we can do the above loop twice
    p("jns done_{}".format(SALT))
    p("add ${}, {}".format(32 * 22, a_mem))
    if a_mem != b_mem:  # we would not want to modify the same pointer twice
        p("add ${}, {}".format(32 * 22, b_mem))
    p("add ${}, {}".format(32 * 44, r_mem))
    p("jmp innerloop_{}".format(SALT))
    p("done_{}:".format(SALT))  # this label is used so we do not do unnecessary additions on the last loop

    p("sub ${}, {}".format(32 * 22, a_mem))
    if a_mem != b_mem:
        p("sub ${}, {}".format(32 * 22, b_mem))
    p("sub ${}, {}".format(32 * 44, r_mem))

    for i in range(22):
        p("vmovdqa {}({}), %ymm{}".format(32*(i+a_off), a_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(22 + i + a_off), a_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(a_in_rsp + i)))

        p("vmovdqa {}({}), %ymm{}".format(32*(i+b_off), b_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(22 + i+b_off), b_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(b_in_rsp + i)))

    mul_64x11('%rsp', '%rsp', '%rsp', t2_in_rsp, a_in_rsp, b_in_rsp)
    mul_64x11('%rsp', '%rsp', '%rsp', t2_in_rsp + 22, a_in_rsp + 11, b_in_rsp + 11)
    mul_64x11('%rsp', '%rsp', '%rsp', a_b_summed, a_in_rsp, b_in_rsp, additive=True)

    for i in range(10):
        # t2b.coeffs[11 + i] -= t2b.coeffs[22 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+11+i), t0))
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+22+i), t0, t0))

        # t2b.coeffs[22 + i] = t2.coeffs[11 + i] - t2b.coeffs[11 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(11+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # t2b.coeffs[22 + i] -= t2b.coeffs[33 + i];
        # store t2b.coeffs[22 + i] in a register for later use during recomposition
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+33+i), t1, 6+i))

        # t2b.coeffs[11 + i] -= t2b.coeffs[i];
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + i), t0, t0))

        # t2b.coeffs[11 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(t2_in_rsp+11+i)))

    # t2b.coeffs[21] = t2.coeffs[10] - t2b.coeffs[10] - t2b.coeffs[32];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(10+a_b_summed), t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 10), t0, t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 32), t0, t0))

    # compose outer layer Karatsuba (t2b.coeffs[21] is still in t0)
    # r->coeffs[43] = t2b.coeffs[21] - r->coeffs[21] - r->coeffs[65];
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(21+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(65+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(43+r_off), r_mem))

    for i in range(21):
        # r->coeffs[22 + i] -= r->coeffs[44 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(22+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(44+i+r_off), r_mem, t0, t0))

        # r->coeffs[44 + i] = t2b.coeffs[22 + i] - r->coeffs[22 + i];
        if i < 10:  # we still have a few stored in registers
            t1 = 6+i
        else:
            t1 = 1
            p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+22+i), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[44 + i] -= r->coeffs[66 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(66+i+r_off), r_mem, t1, t1))

        # r->coeffs[22 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[22 + i] += t2b.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+i), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(22+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(44+i+r_off), r_mem))

    # explicitly zero out the 88th coefficient, as this makes it much nicer
    # to deal with these results in a vectorized way when interpolating.
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t1, t1))
    p("vmovdqa %ymm{}, {}({})".format(t1, 32*(87+r_off), r_mem))

    if transpose:
        transpose_16x96_to_96x16(dst=r_real, src=r_mem, src_off=r_transpose)

    p("add ${}, {}".format(2*16 * coeffs, a_real))
    p("add ${}, {}".format(2*16 * coeffs, b_real))
    p("add ${}, {}".format(2*16 * coeffs*2, r_real))
    p("dec %ecx")
    p("jnz karatsuba_loop_{}".format(SALT))
    # restore the original value of r_real to prevent caller confusion
    p("sub ${}, {}".format(4 * (2*16 * coeffs*2), r_real))
    p("add ${}, %rsp".format((44 + 44 + 96 + 22 + 22 + 22 + 44) * 32))

if __name__ == '__main__':
    p(".data")
    p(".align 32")

    p(".text")
    p(".global K2_K2_schoolbook_64x44coef")
    p(".global K2_K2_schoolbook_64x44coef_transpose")
    p(".att_syntax prefix")

    p("K2_K2_schoolbook_64x44coef:")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    K2_K2_transpose_64x44(transpose=False)

    p("mov %r8, %rsp")
    p("ret")

    p("K2_K2_schoolbook_64x44coef_transpose:")

    p("mov %rsp, %r8")  # Use r8 to store the old stack pointer during execution.
    p("andq $-32, %rsp")  # Align rsp to the next 32-byte value, for vmovdqa.

    K2_K2_transpose_64x44()

    p("mov %r8, %rsp")
    p("ret")
