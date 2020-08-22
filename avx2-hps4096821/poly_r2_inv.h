#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

#define poly_R2_tobytes CRYPTO_NAMESPACE(poly_R2_tobytes)
#define poly_R2_frombytes CRYPTO_NAMESPACE(poly_R2_frombytes)
void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

#define square_1_821 CRYPTO_NAMESPACE(square_1_821)
#define square_3_821 CRYPTO_NAMESPACE(square_3_821)
#define square_6_821 CRYPTO_NAMESPACE(square_6_821)
#define square_12_821 CRYPTO_NAMESPACE(square_12_821)
#define square_24_821 CRYPTO_NAMESPACE(square_24_821)
#define square_51_821 CRYPTO_NAMESPACE(square_51_821)
#define square_102_821 CRYPTO_NAMESPACE(square_102_821)
#define square_204_821 CRYPTO_NAMESPACE(square_204_821)
#define square_408_821 CRYPTO_NAMESPACE(square_408_821)
extern void square_1_821(unsigned char* out, const unsigned char* a);
extern void square_3_821(unsigned char* out, const unsigned char* a);
extern void square_6_821(unsigned char* out, const unsigned char* a);
extern void square_12_821(unsigned char* out, const unsigned char* a);
extern void square_24_821(unsigned char* out, const unsigned char* a);
extern void square_51_821(unsigned char* out, const unsigned char* a);
extern void square_102_821(unsigned char* out, const unsigned char* a);
extern void square_204_821(unsigned char* out, const unsigned char* a);
extern void square_408_821(unsigned char* out, const unsigned char* a);

#define poly_R2_mul CRYPTO_NAMESPACE(poly_R2_mul)
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);
#endif
