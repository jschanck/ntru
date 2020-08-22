#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

#define poly_R2_tobytes CRYPTO_NAMESPACE(poly_R2_tobytes)
#define poly_R2_frombytes CRYPTO_NAMESPACE(poly_R2_frombytes)
void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

#define square_1_677 CRYPTO_NAMESPACE(square_1_677)
#define square_2_677 CRYPTO_NAMESPACE(square_2_677)
#define square_3_677 CRYPTO_NAMESPACE(square_3_677)
#define square_5_677 CRYPTO_NAMESPACE(square_5_677)
#define square_10_677 CRYPTO_NAMESPACE(square_10_677)
#define square_21_677 CRYPTO_NAMESPACE(square_21_677)
#define square_42_677 CRYPTO_NAMESPACE(square_42_677)
#define square_84_677 CRYPTO_NAMESPACE(square_84_677)
#define square_168_677 CRYPTO_NAMESPACE(square_168_677)
#define square_336_677 CRYPTO_NAMESPACE(square_336_677)
extern void square_1_677(unsigned char* out, const unsigned char* a);
extern void square_2_677(unsigned char* out, const unsigned char* a);
extern void square_3_677(unsigned char* out, const unsigned char* a);
extern void square_5_677(unsigned char* out, const unsigned char* a);
extern void square_10_677(unsigned char* out, const unsigned char* a);
extern void square_21_677(unsigned char* out, const unsigned char* a);
extern void square_42_677(unsigned char* out, const unsigned char* a);
extern void square_84_677(unsigned char* out, const unsigned char* a);
extern void square_168_677(unsigned char* out, const unsigned char* a);
extern void square_336_677(unsigned char* out, const unsigned char* a);

#define poly_R2_mul CRYPTO_NAMESPACE(poly_R2_mul)
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);

#endif
