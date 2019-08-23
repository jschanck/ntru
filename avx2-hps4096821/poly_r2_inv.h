#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

extern void square_1_821(unsigned char* out, const unsigned char* a);
extern void square_3_821(unsigned char* out, const unsigned char* a);
extern void square_6_821(unsigned char* out, const unsigned char* a);
extern void square_12_821(unsigned char* out, const unsigned char* a);
extern void square_24_821(unsigned char* out, const unsigned char* a);
extern void square_51_821(unsigned char* out, const unsigned char* a);
extern void square_102_821(unsigned char* out, const unsigned char* a);
extern void square_204_821(unsigned char* out, const unsigned char* a);
extern void square_408_821(unsigned char* out, const unsigned char* a);
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);

#endif
