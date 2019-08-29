p = print

def mod3_masks():
    p("mask_ff:")
    for i in range(16):
        p(".word 0xff")
    p("mask_f:")
    for i in range(16):
        p(".word 0xf")
    p("mask_3:")
    for i in range(16):
        p(".word 0x03")

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
