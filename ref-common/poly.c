#include "poly.h"

/* Map {0, 1, 2} -> {0,1,q-1} in place */
void poly_Z3_to_Zq(poly *r)
{
  int i;
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = r->coeffs[i] | ((-(r->coeffs[i]>>1)) & (NTRU_Q-1));
}

/* Map {0, 1, q-1} -> {0,1,2} in place */
void poly_trinary_Zq_to_Z3(poly *r)
{
  int i;
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = 3 & (r->coeffs[i] ^ (r->coeffs[i]>>(NTRU_LOGQ-1)));
}

void poly_Rq_mul(poly *r, const poly *a, const poly *b)
{
  int k,i;

  for(k=0; k<NTRU_N; k++)
  {
    r->coeffs[k] = 0;
    for(i=1; i<NTRU_N-k; i++)
      r->coeffs[k] += a->coeffs[k+i] * b->coeffs[NTRU_N-i];
    for(i=0; i<k+1; i++)
      r->coeffs[k] += a->coeffs[k-i] * b->coeffs[i];
    r->coeffs[k] = MODQ(r->coeffs[k]);
  }
}

void poly_Sq_mul(poly *r, const poly *a, const poly *b)
{
  int i;
  poly_Rq_mul(r, a, b);
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = MODQ(r->coeffs[i] - r->coeffs[NTRU_N-1]);
}

void poly_S3_mul(poly *r, const poly *a, const poly *b)
{
  int k,i;

  for(k=0; k<NTRU_N; k++)
  {
    r->coeffs[k] = 0;
    for(i=1; i<NTRU_N-k; i++)
      r->coeffs[k] += a->coeffs[k+i] * b->coeffs[NTRU_N-i];
    for(i=0; i<k+1; i++)
      r->coeffs[k] += a->coeffs[k-i] * b->coeffs[i];
  }
  for(k=0; k<NTRU_N; k++)
    r->coeffs[k] = r->coeffs[k] + 2*r->coeffs[NTRU_N-1];
  poly_mod3(r);
}

void poly_Rq_mul_x_minus_1(poly *r, const poly *a)
{
  int i;
  uint16_t last_coeff = a->coeffs[NTRU_N-1];

  for (i = NTRU_N - 1; i > 0; i--) {
    r->coeffs[i] = MODQ(a->coeffs[i-1] + (NTRU_Q - a->coeffs[i]));
  }
  r->coeffs[0] = MODQ(last_coeff + (NTRU_Q - a->coeffs[0]));
}

#ifdef NTRU_HPS
void poly_lift(poly *r, const poly *a)
{
  int i;
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = a->coeffs[i];
  poly_Z3_to_Zq(r);
}
#endif

#ifdef NTRU_HRSS
void poly_lift(poly *r, const poly *a)
{
  /* NOTE: Assumes input is in {0,1,2}^N */
  /*       Produces output in [0,Q-1]^N */
  int i;
  poly b;
  uint16_t t, zj;

  /* Define z by <z*x^i, x-1> = delta_{i,0} mod 3:      */
  /*   t      = -1/N mod p = -N mod 3                   */
  /*   z[0]   = 2 - t mod 3                             */
  /*   z[1]   = 0 mod 3                                 */
  /*   z[j]   = z[j-1] + t mod 3                        */
  /* We'll compute b = a/(x-1) mod (3, Phi) using       */
  /*   b[0] = <z, a>, b[1] = <z*x,a>, b[2] = <z*x^2,a>  */
  /*   b[i] = b[i-3] - (a[i] + a[i-1] + a[i-2])         */
  t = 3 - (NTRU_N % 3);
  b.coeffs[0] = a->coeffs[0] * (2-t) + a->coeffs[1] * 0 + a->coeffs[2] * t;
  b.coeffs[1] = a->coeffs[1] * (2-t) + a->coeffs[2] * 0;
  b.coeffs[2] = a->coeffs[2] * (2-t);

  zj = 0; /* z[1] */
  for(i=3; i<NTRU_N; i++)
  {
    b.coeffs[0] += a->coeffs[i] * (zj + 2*t);
    b.coeffs[1] += a->coeffs[i] * (zj + t);
    b.coeffs[2] += a->coeffs[i] * zj;
    zj = (zj + t) % 3;
  }
  b.coeffs[1] += a->coeffs[0] * (zj + t);
  b.coeffs[2] += a->coeffs[0] * zj;
  b.coeffs[2] += a->coeffs[1] * (zj + t);

  b.coeffs[0] = b.coeffs[0];
  b.coeffs[1] = b.coeffs[1];
  b.coeffs[2] = b.coeffs[2];
  for(i=3; i<NTRU_N; i++)
    b.coeffs[i] =
      b.coeffs[i-3] + 2*(a->coeffs[i] + a->coeffs[i-1] + a->coeffs[i-2]);

  /* Finish reduction mod Phi by subtracting Phi * b[N-1] */
  for(i=0; i<NTRU_N; i++)
    b.coeffs[i] = b.coeffs[i] + 2*b.coeffs[NTRU_N-1];
  poly_mod3(&b);

  /* Switch from {0,1,2} to {0,1,q-1} coefficient representation */
  poly_Z3_to_Zq(&b);

  /* Multiply by (x-1) */
  poly_Rq_mul_x_minus_1(r, &b);
}
#endif

void poly_Rq_to_S3(poly *r, const poly *a)
{
  /* NOTE: Assumes input is in [0,Q-1]^N */
  /*       Produces output in {0,1,2}^N */
  int i;

  /* Center coeffs around 3Q: [0, Q-1] -> [3Q - Q/2, 3Q + Q/2) */
  for(i=0; i<NTRU_N; i++)
  {
    r->coeffs[i] = ((a->coeffs[i] >> (NTRU_LOGQ-1)) ^ 3) << NTRU_LOGQ;
    r->coeffs[i] += a->coeffs[i];
  }
  /* Reduce mod (3, Phi) */
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = r->coeffs[i] + 2*r->coeffs[NTRU_N-1];
  poly_mod3(r);
}

static void poly_R2_inv_to_Rq_inv(poly *r, const poly *ai, const poly *a)
{
#if NTRU_Q <= 256 || NTRU_Q >= 65536
#error "poly_R2_inv_to_Rq_inv in poly.c assumes 256 < q < 65536"
#endif

  int i;
  poly b, c;
  poly s;

  // for 0..4
  //    ai = ai * (2 - a*ai)  mod q
  for(i=0; i<NTRU_N; i++)
    b.coeffs[i] = MODQ(NTRU_Q - a->coeffs[i]); // b = -a

  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = ai->coeffs[i];

  poly_Rq_mul(&c, r, &b);
  c.coeffs[0] += 2; // c = 2 - a*ai
  poly_Rq_mul(&s, &c, r); // s = ai*c

  poly_Rq_mul(&c, &s, &b);
  c.coeffs[0] += 2; // c = 2 - a*s
  poly_Rq_mul(r, &c, &s); // r = s*c

  poly_Rq_mul(&c, r, &b);
  c.coeffs[0] += 2; // c = 2 - a*r
  poly_Rq_mul(&s, &c, r); // s = r*c

  poly_Rq_mul(&c, &s, &b);
  c.coeffs[0] += 2; // c = 2 - a*s
  poly_Rq_mul(r, &c, &s); // r = s*c
}

void poly_Rq_inv(poly *r, const poly *a)
{
  poly ai2;
  poly_R2_inv(&ai2, a);
  poly_R2_inv_to_Rq_inv(r, &ai2, a);
}
