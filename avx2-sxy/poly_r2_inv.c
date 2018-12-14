#include "poly_r2_inv.h"
#include "poly.h"

// TODO this costs 1764 cycles.. (implementing as S3_to_bytes results in 2108)
// This can be implemented nicely in assembly using pdep / pext functions
void poly_R2_tobytes(unsigned char *out, const poly *a)
{
  #if NTRU_N != 701
    #error This function requires NTRU_N = 701!
  #endif
  int i, j, k;
  for (i = 0; i < 12; i++) {
    for (k = 0; k < 8; k++) {
      out[i*8+k] = 0;
      for (j = 0; j < 8; j++) {
        if ((i*8+k)*8 + j < NTRU_N) {
          out[i*8+k] |= (a->coeffs[(i*8+k)*8 + j] & 1) << j;
        }
      }
    }
  }
}

void poly_R2_frombytes(poly *a, const unsigned char *in)
{
  #if NTRU_N != 701
    #error This function requires NTRU_N = 701!
  #endif
  int i, j, k;
  for (i = 0; i < 12; i++) {
    for (k = 0; k < 8; k++) {
      for (j = 0; j < 8; j++) {
        if ((i*8+k)*8 + j < NTRU_N) {
          a->coeffs[(i*8+k)*8 + j] = (in[i*8+k] >> j) & 1;
        }
      }
    }
  }
}

int poly_R2_inv(poly *r, const poly *a) {
    #if NTRU_N != 701
      #error This function requires NTRU_N = 701!
    #endif
    unsigned char squares[13][96] __attribute__((aligned(32)));

    // This relies on the following addition chain:
    // 1, 2, 3, 6, 12, 15, 27, 42, 84, 168, 336, 672, 699

    poly_R2_tobytes(squares[0], a); // TODO alignment

    square_1_701(squares[1], squares[0]);
    poly_R2_mul(squares[1], squares[1], squares[0]);
    square_1_701(squares[2], squares[1]);
    poly_R2_mul(squares[2], squares[2], squares[0]);
    square_3_701(squares[3], squares[2]);
    poly_R2_mul(squares[3], squares[3], squares[2]);
    square_6_701(squares[4], squares[3]);
    poly_R2_mul(squares[4], squares[4], squares[3]);
    square_3_701(squares[5], squares[4]);
    poly_R2_mul(squares[5], squares[5], squares[2]);
    square_12_701(squares[6], squares[5]);
    poly_R2_mul(squares[6], squares[6], squares[4]);
    square_15_701(squares[7], squares[6]);
    poly_R2_mul(squares[7], squares[7], squares[5]);
    square_42_701(squares[8], squares[7]);
    poly_R2_mul(squares[8], squares[8], squares[7]);
    square_84_701(squares[9], squares[8]);
    poly_R2_mul(squares[9], squares[9], squares[8]);
    square_168_701(squares[10], squares[9]);
    poly_R2_mul(squares[10], squares[10], squares[9]);
    square_336_701(squares[11], squares[10]);
    poly_R2_mul(squares[11], squares[11], squares[10]);
    square_27_701(squares[12], squares[11]);
    poly_R2_mul(squares[12], squares[12], squares[6]);
    square_1_701(squares[0], squares[12]);

    poly_R2_frombytes(r, squares[0]);
    return 0;
}
