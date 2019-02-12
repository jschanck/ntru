#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

extern void square_1_701(unsigned char* out, const unsigned char* a);
extern void square_3_701(unsigned char* out, const unsigned char* a);
extern void square_6_701(unsigned char* out, const unsigned char* a);
extern void square_12_701(unsigned char* out, const unsigned char* a);
extern void square_15_701(unsigned char* out, const unsigned char* a);
extern void square_27_701(unsigned char* out, const unsigned char* a);
extern void square_42_701(unsigned char* out, const unsigned char* a);
extern void square_84_701(unsigned char* out, const unsigned char* a);
extern void square_168_701(unsigned char* out, const unsigned char* a);
extern void square_336_701(unsigned char* out, const unsigned char* a);
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);

int poly_R2_inv(poly *r, const poly *a);

#endif
