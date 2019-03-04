#ifndef POLY_H
#define POLY_H

#include <stdint.h>
#include <stdlib.h>
#include "params.h"

#define MODQ(X) ((X) & (NTRU_Q-1))
uint16_t mod3(uint16_t a);

typedef struct{
  // round to nearest multiple of 32 to make it easier to load into vector
  //   registers without having to do bound checks
  #define NTRU_N_32 ((NTRU_N + 31) / 32) * 32
  uint16_t coeffs[NTRU_N_32] __attribute__((aligned(32)));
} poly;

void poly_Sq_tobytes(unsigned char *r, const poly *a);
void poly_Sq_frombytes(poly *r, const unsigned char *a);

void poly_Rq_sum_zero_tobytes(unsigned char *r, const poly *a);
void poly_Rq_sum_zero_frombytes(poly *r, const unsigned char *a);

void poly_S3_tobytes(unsigned char msg[NTRU_PACK_TRINARY_BYTES], const poly *r);
void poly_S3_frombytes(poly *r, const unsigned char msg[NTRU_PACK_TRINARY_BYTES]);

void poly_Sq_mul(poly *r, const poly *a, const poly *b);
void poly_Rq_mul(poly *r, const poly *a, const poly *b);
void poly_Rq_mul_x_minus_1(poly *r, const poly *a);
void poly_S3_mul(poly *r, const poly *a, const poly *b);
void poly_lift(poly *r, const poly *a);
void poly_Rq_to_S3(poly *r, const poly *a);

void poly_Rq_inv(poly *r, const poly *a);
void poly_S3_inv(poly *r, const poly *a);

void poly_Z3_to_Zq(poly *r);
void poly_trinary_Zq_to_Z3(poly *r);

#endif
