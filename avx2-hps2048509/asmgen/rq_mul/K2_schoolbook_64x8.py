p = print

def K2_schoolbook_64x8(r_mem, a_mem, b_mem, r_off=0, a_off=0, b_off=0, additive=False):
    # Multiply two polynomials with 4 coefficients to form a polynomial with 8 coefficients
    # using the schoolbook method. This is the first multiplication necessary in karatsuba.
    for i in range(4):
        p("vmovdqa {}({}), %ymm{}".format(32*(i + a_off), a_mem, i))
        p("vmovdqa {}({}), %ymm{}".format(32*(i + b_off), b_mem, i+4))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off + 8), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 8), b_mem, i+4, i+4))
    for i in range(7):
        first = True
        for j in range(min(i+1, 4)):
            if i - j < 4:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, 12 + (i % 2)))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, 15))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(12 + (i % 2), 15, 12 + (i % 2)))
        p("vmovdqa %ymm{}, {}({})".format(12 + (i % 2), 32*(i + r_off), r_mem))

    # Multiply another two polynomials with 4 coefficients to form a polynomial with 8 coefficients
    # using the schoolbook method. This is the second multiplication necessary in karatsuba.
    for i in range(4):
        p("vmovdqa {}({}), %ymm{}".format(32*(4+i + a_off), a_mem, i))
        p("vmovdqa {}({}), %ymm{}".format(32*(4+i + b_off), b_mem, i+4))
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(4+i + a_off + 8), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(4+i + b_off + 8), b_mem, i+4, i+4))
    for i in range(7):
        first = True
        for j in range(min(i+1, 4)):
            if i - j < 4:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, 12 + (i % 2)))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, 15))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(12 + (i % 2), 15, 12 + (i % 2)))
        p("vmovdqa %ymm{}, {}({})".format(12 + (i % 2), 32*(8+i + r_off), r_mem))

    # Add upper and lower half of both 8 coefficient polynomials. These are the additions
    # needed before the last multiplication can happen in karatsuba.
    for i in range(4):
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off), a_mem, i, i))
        p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off), b_mem, i+4, i+4))
        # these additions should not be strictly necessary, as we already computed this earlier
        # recomputing seems more convenient than storing them
        if additive:
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + a_off + 8), a_mem, i, i))
            p("vpaddw {}({}), %ymm{}, %ymm{}".format(32*(i + b_off + 8), b_mem, i+4, i+4))

    # At this point ymm0 through ymm7 are taken due to the additions. We can use ymm9 through ymm15
    # to store the resulting multiplication. We have ymm8 free for intermediate computations
    # which means we can do the multiplication without doing anything fancy or using the stack!
    free = 8
    for i in range(7):
        target = 9+i
        first = True
        for j in range(min(i+1, 4)):
            if i - j < 4:
                if first:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, target))
                    first = False
                else:
                    p("vpmullw %ymm{}, %ymm{}, %ymm{}".format(j, 4+ i-j, free))
                    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(free, target, target))

    # Compute the subtractions necessary in karatsuba and add the result to the correct
    # location in memory to complete karatsuba.
    for i in range(7):
        # First subtraction. Store last 3 in registers to save memory accesses later during addition.
        if i < 4:
            p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(i + r_off), r_mem, 9+i, 9+i))
        else:
            p("vmovdqa {}({}), %ymm{}".format(32*(i + r_off), r_mem, i-4))
            p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(i-4, 9+i, 9+i))

        # Second subtraction. Store first 3 in registers to save memory accesses later during addition.
        if i < 3:
            p("vmovdqa {}({}), %ymm{}".format(32*(8+i + r_off), r_mem, i+3))
            p("vpsubw %ymm{}, %ymm{}, %ymm{}".format(i+3, 9+i, 9+i))
        else:
            p("vpsubw {}({}), %ymm{}, %ymm{}".format(32*(8+i + r_off), r_mem, 9+i, 9+i))

    # Add two parts of karatsuba that were already in memory (which are now in registers) and then store
    # the final polynomial.
    for i in range(7):
        if i < 3:
            p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(i, 9+i, 9+i))
        elif i > 3:
            p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(i-1, 9+i, 9+i))
        # The middle piece (i == 3) isn't affected by the two halves so no need to add anything to it.

        p("vmovdqa %ymm{}, {}({})".format(9+i, 32*(4+i + r_off), r_mem))
