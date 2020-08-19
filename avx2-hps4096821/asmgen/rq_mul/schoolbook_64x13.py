p = print

def schoolbook_64x13(r_mem, a_mem, b_mem, r_off=0, a_off=0, b_off=0, additive=False):
    # Load a[0:6] into ymm0-ymm6
    # Load b[0:6] into ymm7-ymm13
    # if "additive": add a[13:19] to ymm0-6, b[13:19] to ymm7-13
    for i in range(7):
        p("vmovdqa {}({}), %ymm{}".format(32*(i + a_off), a_mem, i))
        p("vmovdqa {}({}), %ymm{}".format(32*(i + b_off), b_mem, i+7))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off + 13), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 13), b_mem, i+7, i+7))
    # multiply all pairs ymm0-6 x ymm7-13
    for i in range(13):
        first = True
        for j in range(min(i+1, 7)):
            if i - j < 7:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 7+ i-j, 14))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 7+ i-j, 15))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(14, 15, 14))
        p("vmovdqa %ymm{}, {}({})".format(14, 32*(i + r_off), r_mem))

    # Load b[7:12] into ymm7-ymm12, keep b[6] in ymm13 until fourth loop
    for i in range(6):
        p("vmovdqa {}({}), %ymm{}".format(32*(7+i + b_off), b_mem, i+7))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(7+i + b_off + 13), b_mem, i+7, i+7))
    # multiply all pairs ymm0-6 x ymm7-12
    for i in range(12):
        first = True
        for j in range(min(i+1, 7)):
            if i - j < 6:
                if first and 7+i < 13:
                    p("vmovdqa {}({}), %ymm{}".format(32*(7+i + r_off), r_mem, 14))
                    first = False
                if first and 7+i >= 13:
                    p("vpxor %ymm14, %ymm14, %ymm14")
                    first = False
                p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 7+ i-j, 15))
                p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(14, 15, 14))
        p("vmovdqa %ymm{}, {}({})".format(14, 32*(7+i + r_off), r_mem))

    # Load a[7:12] into ymm0-ymm5
    for i in range(6):
        p("vmovdqa {}({}), %ymm{}".format(32*(7+i + a_off), a_mem, i))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(7+i + a_off + 13), a_mem, i, i))
    # multiply all pairs ymm0-5 x ymm7-12
    for i in range(11):
        first = True
        for j in range(min(i+1, 6)):
            if i - j < 6:
                if first and 14+i < 19:
                    p("vmovdqa {}({}), %ymm{}".format(32*(14+i + r_off), r_mem, 14))
                    first = False
                if first and 14+i >= 19:
                    p("vpxor %ymm14, %ymm14, %ymm14")
                    first = False
                p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 7+ i-j, 15))
                p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(14, 15, 14))
        p("vmovdqa %ymm{}, {}({})".format(14, 32*(14+i + r_off), r_mem))

    # Load b[0:5] into ymm7-ymm12. already have b[6] in ymm13.
    for i in range(6):
        p("vmovdqa {}({}), %ymm{}".format(32*(i + b_off), b_mem, i+7))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 13), b_mem, i+7, i+7))
    # multiply all pairs ymm0-5 x ymm7-13
    for i in range(12):
        first = True
        for j in range(min(i+1, 6)):
            if i - j < 7:
                if first:
                    p("vmovdqa {}({}), %ymm{}".format(32*(7+i + r_off), r_mem, 14))
                    first = False
                p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 7+ i-j, 15))
                p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(14, 15, 14))
        p("vmovdqa %ymm{}, {}({})".format(14, 32*(7+i + r_off), r_mem))



if __name__ == '__main__':
    p(".data")
    p(".p2align 5")

    p(".text")
    p(".global schoolbook_64x13")
    p(".global _schoolbook_64x13")
    p(".global schoolbook_64x13_additive")
    p(".global _schoolbook_64x13_additive")

    p("schoolbook_64x13:")
    p("mov $4, %ecx")

    p("karatsuba_64x13_loop:")
    schoolbook_64x13('%rdi', '%rsi', '%rdx')
    p("add $1664, %rsi")
    p("add $1664, %rdx")
    p("add $3328, %rdi")
    p("dec %ecx")
    p("jnz karatsuba_64x13_loop")

    p("ret")

    p("schoolbook_64x13_additive:")
    p("mov $4, %ecx")

    p("karatsuba_64x13_loop_additive:")
    schoolbook_64x13('%rdi', '%rsi', '%rdx', additive=True)
    p("add $1664, %rsi")
    p("add $1664, %rdx")
    p("add $3328, %rdi")
    p("dec %ecx")
    p("jnz karatsuba_64x13_loop_additive")

    p("ret")
