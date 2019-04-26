
from K2_schoolbook_64x8 import K2_schoolbook_64x8 as mul_64x8
from transpose import transpose_32x16_to_16x32, transpose_16x64_to_64x16
import random

p = print

def K2_K2_transpose_64x32(r_real='%rdi', a_real='%rsi', b_real='%rdx', coeffs=32):
    # allocate space for;
    # - (A[0:8]+B[0:8])*(C[0:8]+D[0:8]) inside K2-step
    # - (a[0:16] + a[16:32]) before 3rd K2-step
    # - (b[0:16] + b[16:32]) before 3rd K2-step
    # - output of third 16x16 multiplication

    SALT = '{:16x}'.format(random.randint(0, 2**128))  # prevent duplicate labels

    p("subq ${}, %rsp".format((32 + 32 + 64 + 16 + 16 + 16 + 32) * 32))
    a_transpose = 0
    b_transpose = a_transpose + 32
    r_transpose = b_transpose + 32
    a_b_summed = r_transpose + 64
    a_in_rsp = a_b_summed + 16
    b_in_rsp = a_in_rsp + 16
    t2_in_rsp = b_in_rsp + 16

    t0 = 0
    t1 = 1
    p("mov $4, %ecx")
    p("karatsuba_loop_{}:".format(SALT))

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

    transpose_32x16_to_16x32(dst=a_mem, src=a_real, dst_off=a_off)
    transpose_32x16_to_16x32(dst=b_mem, src=b_real, dst_off=b_off)

    p("innerloop_{}:".format(SALT))

    mul_64x8(r_mem, a_mem, b_mem, r_off, a_off, b_off)
    mul_64x8(r_mem, a_mem, b_mem, r_off+16, a_off+8, b_off+8)
    mul_64x8('%rsp', a_mem, b_mem, a_b_summed, a_off, b_off, additive=True)

    # r->coeffs[15] = t2.coeffs[7] - r->coeffs[7] - r->coeffs[23];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(7+a_b_summed), t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(7+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(23+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(15+r_off), r_mem))

    for i in range(7):
        # r->coeffs[8 + i] -= r->coeffs[16 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(8+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(16+i+r_off), r_mem, t0, t0))

        # r->coeffs[16 + i] = t2.coeffs[8 + i] - r->coeffs[8 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(8+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[16 + i] -= r->coeffs[24 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(24+i+r_off), r_mem, t1, t1))

        # r->coeffs[8 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[8 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(8+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(16+i+r_off), r_mem))

    p("neg %ecx")  # abuse ecx as toggle so we can do the above loop twice
    p("jns done_{}".format(SALT))
    p("add ${}, {}".format(32 * 16, a_mem))
    if a_mem != b_mem:  # we would not want to modify the same pointer twice
        p("add ${}, {}".format(32 * 16, b_mem))
    p("add ${}, {}".format(32 * 32, r_mem))
    p("jmp innerloop_{}".format(SALT))
    p("done_{}:".format(SALT))  # this label is used so we do not do unnecessary additions on the last loop

    p("sub ${}, {}".format(32 * 16, a_mem))
    if a_mem != b_mem:
        p("sub ${}, {}".format(32 * 16, b_mem))
    p("sub ${}, {}".format(32 * 32, r_mem))

    for i in range(16):
        p("vmovdqa {}({}), %ymm{}".format(32*(i+a_off), a_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(16 + i + a_off), a_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(a_in_rsp + i)))

        p("vmovdqa {}({}), %ymm{}".format(32*(i+b_off), b_mem, t0))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(16 + i + b_off), b_mem, t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(b_in_rsp + i)))

    mul_64x8('%rsp', '%rsp', '%rsp', t2_in_rsp, a_in_rsp, b_in_rsp)
    mul_64x8('%rsp', '%rsp', '%rsp', t2_in_rsp + 16, a_in_rsp + 8, b_in_rsp + 8)
    mul_64x8('%rsp', '%rsp', '%rsp', a_b_summed, a_in_rsp, b_in_rsp, additive=True)

    for i in range(7):
        # t2b.coeffs[8 + i] -= t2b.coeffs[16 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+8+i), t0))
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+16+i), t0, t0))

        # t2b.coeffs[16 + i] = t2.coeffs[8 + i] - t2b.coeffs[8 + i];
        p("vmovdqa {}(%rsp), %ymm{}".format(32*(8+i+a_b_summed), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # t2b.coeffs[16 + i] -= t2b.coeffs[24 + i];
        # store t2b.coeffs[16 + i] in a register for later use during recomposition
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+24+i), t1, 6+i))

        # t2b.coeffs[8 + i] -= t2b.coeffs[i];
        p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + i), t0, t0))

        # t2b.coeffs[8 + i] += t2.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(i+a_b_summed), t0, t0))
        p("vmovdqa %ymm{}, {}(%rsp)".format(t0, 32*(t2_in_rsp+8+i)))

    # t2b.coeffs[15] = t2.coeffs[7] - t2b.coeffs[7] - t2b.coeffs[23];
    p("vmovdqa {}(%rsp), %ymm{}".format(32*(7+a_b_summed), t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 7), t0, t0))
    p("vpsubw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp + 23), t0, t0))

    # compose outer layer Karatsuba (t2b.coeffs[15] is still in t0)
    # r->coeffs[31] = t2b.coeffs[15] - r->coeffs[15] - r->coeffs[47];
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(15+r_off), r_mem, t0, t0))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(47+r_off), r_mem, t0, t0))
    p("vmovdqa %ymm{}, {}({})".format(t0, 32*(31+r_off), r_mem))

    for i in range(15):
        # r->coeffs[16 + i] -= r->coeffs[32 + i];
        p("vmovdqa {}({}), %ymm{}".format(32*(16+i+r_off), r_mem, t0))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(32+i+r_off), r_mem, t0, t0))

        # r->coeffs[32 + i] = t2b.coeffs[16 + i] - r->coeffs[16 + i];
        if i < 7:  # we still have a few stored in registers
            t1 = 6+i
        else:
            t1 = 1
            p("vmovdqa {}(%rsp), %ymm{}".format(32*(t2_in_rsp+16+i), t1))
        p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(t0, t1, t1))

        # r->coeffs[32 + i] -= r->coeffs[48 + i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(48+i+r_off), r_mem, t1, t1))

        # r->coeffs[16 + i] -= r->coeffs[i];
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i+r_off), r_mem, t0, t0))

        # r->coeffs[16 + i] += t2b.coeffs[i];
        p("vpaddw {}(%rsp), %ymm{}, %ymm{}".format(32*(t2_in_rsp+i), t0, t0))
        p("vmovdqa %ymm{}, {}({})".format(t0, 32*(16+i+r_off), r_mem))
        p("vmovdqa %ymm{}, {}({})".format(t1, 32*(32+i+r_off), r_mem))

    # explicitly zero out the 64th coefficient, as this makes it much nicer
    # to deal with these results in a vectorized way when interpolating.
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t1, t1, t1))
    p("vmovdqa %ymm{}, {}({})".format(t1, 32*(63+r_off), r_mem))

    transpose_16x64_to_64x16(dst=r_real, src=r_mem, src_off=r_transpose)

    p("add ${}, {}".format(2*16 * coeffs, a_real))
    p("add ${}, {}".format(2*16 * coeffs, b_real))
    p("add ${}, {}".format(2*16 * coeffs*2, r_real))
    p("dec %ecx")
    p("jnz karatsuba_loop_{}".format(SALT))
    # restore the original value of r_real to prevent caller confusion
    p("sub ${}, {}".format(4 * (2*16 * coeffs*2), r_real))
    p("add ${}, %rsp".format((32 + 32 + 64 + 16 + 16 + 16 + 32) * 32))
