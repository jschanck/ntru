
p = print


def mod3(a, r=13, t=14, c=15):
    # r = (a >> 8) + (a & 0xff); // r mod 255 == a mod 255
    p("vpsrlw $8, %ymm{}, %ymm{}".format(a, r))
    p("vpand mask_ff(%rip), %ymm{}, %ymm{}".format(a, a))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 4) + (r & 0xf); // r' mod 15 == r mod 15
    p("vpand mask_f(%rip), %ymm{}, %ymm{}".format(r, a))
    p("vpsrlw $4, %ymm{}, %ymm{}".format(r, r))
    p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    # r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
    for _ in range(2):
        p("vpand mask_3(%rip), %ymm{}, %ymm{}".format(r, a))
        p("vpsrlw $2, %ymm{}, %ymm{}".format(r, r))
        p("vpaddw %ymm{}, %ymm{}, %ymm{}".format(r, a, r))

    #   t = r - 3;
    p("vpsubw mask_3(%rip), %ymm{}, %ymm{}".format(r, t))
    #   c = t >> 15;  t is signed, so shift arithmetic
    p("vpsraw $15, %ymm{}, %ymm{}".format(t, c))

    tmp = a
    #   return (c&r) ^ (~c&t);
    p("vpandn %ymm{}, %ymm{}, %ymm{}".format(t, c, tmp))
    p("vpand %ymm{}, %ymm{}, %ymm{}".format(c, r, t))
    p("vpxor %ymm{}, %ymm{}, %ymm{}".format(t, tmp, r))


from math import ceil

N = 701
N32 = 704

if __name__ == '__main__':
    p(".data")
    p(".section .rodata")
    p(".align 32")

    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")
    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

    p("cast8_to_16:")
    for i in range(8):
      p(".byte 255")
      p(".byte {}".format(i))
    for i in range(8):
      p(".byte 255")
      p(".byte {}".format(i))

    p(".text")
    p(".hidden sample_iid")
    p(".global sample_iid")
    p(".att_syntax prefix")

    p("sample_iid:")
    # rdi holds r
    # rsi holds uniformbytes

    t = 1
    retval = 2
    b = 3
    for i in range(N32//32):
        p("vmovdqu {}(%rsi), %ymm{}".format(i*32, b))
        p("vextracti128 $0, %ymm{}, %xmm{}".format(b, t))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('11' '01' '10' '00', 2), t, t))
        p("vpshufb cast8_to_16(%rip), %ymm{}, %ymm{}".format(t,t))
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, (2*i)*32))

        p("vextracti128 $1, %ymm{}, %xmm{}".format(b, t))
        p("vpermq ${}, %ymm{}, %ymm{}".format(int('11' '01' '10' '00', 2), t, t))
        p("vpshufb cast8_to_16(%rip), %ymm{}, %ymm{}".format(t,t))
        # shuffle
        mod3(t, retval)
        p("vmovdqa %ymm{}, {}(%rdi)".format(retval, (2*i+1)*32))

    for i in range(N-1, N32):
      p("movw $0, {}(%rdi)".format(2*i))
    p("ret")
