#ifndef POLY_R2_INV_H
#define POLY_R2_INV_H

#include "poly.h"

#define poly_R2_tobytes CRYPTO_NAMESPACE(poly_R2_tobytes)
#define poly_R2_frombytes CRYPTO_NAMESPACE(poly_R2_frombytes)
void poly_R2_tobytes(unsigned char *out, const poly *a);
void poly_R2_frombytes(poly *a, const unsigned char *in);

#define square_1_509 CRYPTO_NAMESPACE(square_1_509)
#define square_3_509 CRYPTO_NAMESPACE(square_3_509)
#define square_6_509 CRYPTO_NAMESPACE(square_6_509)
#define square_15_509 CRYPTO_NAMESPACE(square_15_509)
#define square_30_509 CRYPTO_NAMESPACE(square_30_509)
#define square_63_509 CRYPTO_NAMESPACE(square_63_509)
#define square_126_509 CRYPTO_NAMESPACE(square_126_509)
#define square_252_509 CRYPTO_NAMESPACE(square_252_509)
extern void square_1_509(unsigned char* out, const unsigned char* a);
extern void square_3_509(unsigned char* out, const unsigned char* a);
extern void square_6_509(unsigned char* out, const unsigned char* a);
extern void square_15_509(unsigned char* out, const unsigned char* a);
extern void square_30_509(unsigned char* out, const unsigned char* a);
extern void square_63_509(unsigned char* out, const unsigned char* a);
extern void square_126_509(unsigned char* out, const unsigned char* a);
extern void square_252_509(unsigned char* out, const unsigned char* a);

#define poly_R2_mul CRYPTO_NAMESPACE(poly_R2_mul)
extern void poly_R2_mul(unsigned char* out, const unsigned char* a,
                                            const unsigned char* b);
#endif
