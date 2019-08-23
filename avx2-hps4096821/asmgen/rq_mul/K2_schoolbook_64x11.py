p = print


def K2_schoolbook_64x11(r_mem, a_mem, b_mem, r_off=0, a_off=0, b_off=0, additive=False):
    for i in range(6):
        p("vmovdqa {}({}), %ymm{}".format(32*(i + a_off), a_mem, i))
        p("vmovdqa {}({}), %ymm{}".format(32*(i + b_off), b_mem, i+6))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off + 11), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 11), b_mem, i+6, i+6))
    for i in range(11):
        first = True
        for j in range(min(i+1, 6)):
            if i - j < 6:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, 12 + (i % 2)))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, 15))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(12 + (i % 2), 15, 12 + (i % 2)))
        p("vmovdqa %ymm{}, {}({})".format(12 + (i % 2), 32*(i + r_off), r_mem))

    for i in range(5):
        p("vmovdqa {}({}), %ymm{}".format(32*(6+i + a_off), a_mem, i))
        p("vmovdqa {}({}), %ymm{}".format(32*(6+i + b_off), b_mem, i+6))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(6+i + a_off + 11), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(6+i + b_off + 11), b_mem, i+6, i+6))
    for i in range(9):
        first = True
        for j in range(min(i+1, 5)):
            if i - j < 5:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, 12 + (i % 2)))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, 15))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(12 + (i % 2), 15, 12 + (i % 2)))
        p("vmovdqa %ymm{}, {}({})".format(12 + (i % 2), 32*(12+i + r_off), r_mem))

    for i in range(5):  # i == 5 is still in place as a[5] resp. b[5]
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off), a_mem, i, i))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off), b_mem, i+6, i+6))
        # these additions should not be strictly necessary, as we already computed this earlier
        # recomputing seems more convenient than storing them
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off + 11), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 11), b_mem, i+6, i+6))

    # peel apart the third schoolbook mult so we end with (a+b)(c+d) in registers
    # this prevents us from having to touch the stack at all for t2
    i = 5
    target = 12
    free = 15
    for j in range(6):
        if j == 0:
            p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, target))
        else:
            p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, free))
            p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(free, target, target))
    # weird centerpiece, deal with this straight away to free up a register
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(5 + r_off), r_mem, target, target))
    p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(17 + r_off), r_mem, target, target))
    p("vmovdqa %ymm{}, {}({})".format(target, 32*(11 + r_off), r_mem))

    # use a[5] for all products we need it for
    for j in range(1, 5):  # note again that we do not compute [10]
        p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(5, 6+ j, 12+j-1))
    # this frees up register %ymm5 which held a[5]
    free = 5
    # finish up [6] to [9] (in registers 12 to 15)
    for i in range(6, 10):
        target = 12 + i-6  # already contains one product
        for j in range(min(i+1, 6)):
            if j == 5:
                continue  # we've already used a[5]
            if i - j < 6:
                p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, free))
                p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(free, target, target))

    # can now start overwriting b[5], b[4] etc.
    for i in range(4, -1, -1):
        target = 6+i+1  # b[5], b[4], b[3] ..
        first = True
        for j in range(min(i+1, 6)):
            if i - j < 6:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, target))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 6+ i-j, free))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(free, target, target))

    # t2 is now spread all over the registers: (i.e. t[0] in register ymm7)
    t2 = [7, 8, 9, 10, 11, None, 12, 13, 14, 15]

    for i in range(5):
        p("vmovdqa {}({}), %ymm{}".format(32*(6+i + r_off), r_mem, i))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(12+i + r_off), r_mem, i, i))
        if i < 4:
            p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(i, t2[6 + i], i+6))
            if i < 3:
                p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(18+i + r_off), r_mem, i+6, i+6))
            p("vmovdqa %ymm{}, {}({})".format(i+6, 32*(12+i + r_off), r_mem))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(t2[i], i, i))
        p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i + r_off), r_mem, i, i))
        p("vmovdqa %ymm{}, {}({})".format(i, 32*(6+i + r_off), r_mem))


if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")

    p(".text")
    p(".hidden K2_schoolbook_64x11")
    p(".global K2_schoolbook_64x11")
    p(".hidden K2_schoolbook_64x11_additive")
    p(".global K2_schoolbook_64x11_additive")
    p(".att_syntax prefix")

    p("K2_schoolbook_64x11:")
    p("mov $4, %ecx")

    p("karatsuba_64x11_loop:")
    K2_schoolbook_64x11('%rdi', '%rsi', '%rdx')
    p("add $1408, %rsi")
    p("add $1408, %rdx")
    p("add $2816, %rdi")
    p("dec %ecx")
    p("jnz karatsuba_64x11_loop")

    p("ret")

    p("K2_schoolbook_64x11_additive:")
    p("mov $4, %ecx")

    p("karatsuba_64x11_loop_additive:")
    K2_schoolbook_64x11('%rdi', '%rsi', '%rdx', additive=True)
    p("add $1408, %rsi")
    p("add $1408, %rdx")
    p("add $2816, %rdi")
    p("dec %ecx")
    p("jnz karatsuba_64x11_loop_additive")

    p("ret")
