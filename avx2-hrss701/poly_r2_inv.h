#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

#define poly_R2_tobytes CRYPTO_NAMESPACE(poly_R2_tobytes)
#define poly_R2_frombytes CRYPTO_NAMESPACE(poly_R2_frombytes)
void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

#define square_1_701 CRYPTO_NAMESPACE(square_1_701)
#define square_3_701 CRYPTO_NAMESPACE(square_3_701)
#define square_6_701 CRYPTO_NAMESPACE(square_6_701)
#define square_12_701 CRYPTO_NAMESPACE(square_12_701)
#define square_15_701 CRYPTO_NAMESPACE(square_15_701)
#define square_27_701 CRYPTO_NAMESPACE(square_27_701)
#define square_42_701 CRYPTO_NAMESPACE(square_42_701)
#define square_84_701 CRYPTO_NAMESPACE(square_84_701)
#define square_168_701 CRYPTO_NAMESPACE(square_168_701)
#define square_336_701 CRYPTO_NAMESPACE(square_336_701)
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

#define poly_R2_mul CRYPTO_NAMESPACE(poly_R2_mul)
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);
#endif
