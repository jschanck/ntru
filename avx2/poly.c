#include "poly.h"
#include "fips202.h"
#include "poly_r2_inv.h"

extern void poly_Rq_mul(poly *r, const poly *a, const poly *b);
extern void poly_S3_mul(poly *r, const poly *a, const poly *b);
extern void poly_Rq_mul_xm1(poly *r, const poly *a);
extern void poly_S3_inv(poly *r, const poly *a);
extern void poly_Rq_to_S3(poly *r, const poly *a);
extern void poly_S3_to_Rq(poly *r, const poly *a);
extern void cbdS3(poly *r, const uint32_t *buf);

#define MODQ(X) ((X) & (NTRU_Q-1))

/* Map {0, 1, 2} -> {0,1,q-1} */
#define ZP_TO_ZQ(C) \
    (((C) & 1) | ((-((C)>>1)) & (NTRU_Q-1)));

/* Map {0,1,2,4} -> {0,1,2^16-1,1} */
#define ZP_PROD_TO_UINT16(C) \
  (((C) | ((C)>>2)) & 1)  |  (-(((C) & 2)>>1))

uint16_t mod3(uint16_t a)
{
  uint16_t r;
  int16_t t, c;

  r = (a >> 8) + (a & 0xff); // r mod 255 == a mod 255
  r = (r >> 4) + (r & 0xf); // r' mod 15 == r mod 15
  r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3
  r = (r >> 2) + (r & 0x3); // r' mod 3 == r mod 3

  t = r - 3;
  c = t >> 15;

  return (c&r) ^ (~c&t);
}

void poly_Rq_tobytes(unsigned char *r, const poly *a)
{
  int i,j;
  uint16_t t[8];

  for(i=0;i<NTRU_PACK_DEG/8;i++)
  {
    for(j=0;j<8;j++)
      t[j] = a->coeffs[8*i+j];

    r[13*i+ 0] =  t[0]        & 0xff;
    r[13*i+ 1] = (t[0] >>  8) | ((t[1] & 0x07) << 5);
    r[13*i+ 2] = (t[1] >>  3) & 0xff;
    r[13*i+ 3] = (t[1] >> 11) | ((t[2] & 0x3f) << 2);
    r[13*i+ 4] = (t[2] >>  6) | ((t[3] & 0x01) << 7);
    r[13*i+ 5] = (t[3] >>  1) & 0xff;
    r[13*i+ 6] = (t[3] >>  9) | ((t[4] & 0x0f) << 4);
    r[13*i+ 7] = (t[4] >>  4) & 0xff;
    r[13*i+ 8] = (t[4] >> 12) | ((t[5] & 0x7f) << 1);
    r[13*i+ 9] = (t[5] >>  7) | ((t[6] & 0x03) << 6);
    r[13*i+10] = (t[6] >>  2) & 0xff;
    r[13*i+11] = (t[6] >> 10) | ((t[7] & 0x1f) << 3);
    r[13*i+12] = (t[7] >>  5);
  }

  for(j=0;j<NTRU_PACK_DEG-8*i;j++)
    t[j] = a->coeffs[8*i+j];
  for(; j<8; j++)
    t[j] = 0;

  switch(NTRU_PACK_DEG - 8*(NTRU_PACK_DEG/8))
  {
    case 6:
      r[13*i+ 9] = (t[5] >>  7) | ((t[6] & 0x03) << 6);
      r[13*i+ 8] = (t[4] >> 12) | ((t[5] & 0x7f) << 1);
      r[13*i+ 7] = (t[4] >>  4) & 0xff;
    // fallthrough
    case 4:
      r[13*i+ 6] = (t[3] >>  9) | ((t[4] & 0x0f) << 4);
      r[13*i+ 5] = (t[3] >>  1) & 0xff;
      r[13*i+ 4] = (t[2] >>  6) | ((t[3] & 0x01) << 7);
    // fallthrough
    case 2:
      r[13*i+ 3] = (t[1] >> 11) | ((t[2] & 0x3f) << 2);
      r[13*i+ 2] = (t[1] >>  3) & 0xff;
      r[13*i+ 1] = (t[0] >>  8) | ((t[1] & 0x07) << 5);
      r[13*i+ 0] =  t[0]        & 0xff;
  }
}

void poly_Rq_frombytes(poly *r, const unsigned char *a)
{
  int i;
  for(i=0;i<NTRU_PACK_DEG/8;i++)
  {
    r->coeffs[8*i+0] =  a[13*i+ 0]       | (((uint16_t)a[13*i+ 1] & 0x1f) << 8);
    r->coeffs[8*i+1] = (a[13*i+ 1] >> 5) | (((uint16_t)a[13*i+ 2]       ) << 3) | (((uint16_t)a[13*i+ 3] & 0x03) << 11);
    r->coeffs[8*i+2] = (a[13*i+ 3] >> 2) | (((uint16_t)a[13*i+ 4] & 0x7f) << 6);
    r->coeffs[8*i+3] = (a[13*i+ 4] >> 7) | (((uint16_t)a[13*i+ 5]       ) << 1) | (((uint16_t)a[13*i+ 6] & 0x0f) <<  9);
    r->coeffs[8*i+4] = (a[13*i+ 6] >> 4) | (((uint16_t)a[13*i+ 7]       ) << 4) | (((uint16_t)a[13*i+ 8] & 0x01) << 12);
    r->coeffs[8*i+5] = (a[13*i+ 8] >> 1) | (((uint16_t)a[13*i+ 9] & 0x3f) << 7);
    r->coeffs[8*i+6] = (a[13*i+ 9] >> 6) | (((uint16_t)a[13*i+10]       ) << 2) | (((uint16_t)a[13*i+11] & 0x07) << 10);
    r->coeffs[8*i+7] = (a[13*i+11] >> 3) | (((uint16_t)a[13*i+12]       ) << 5);
  }
  switch(NTRU_PACK_DEG - 8*(NTRU_PACK_DEG/8))
  {
    case 6:
      r->coeffs[8*i+5] = (a[13*i+ 8] >> 1) | (((uint16_t)a[13*i+ 9] & 0x3f) << 7);
      r->coeffs[8*i+4] = (a[13*i+ 6] >> 4) | (((uint16_t)a[13*i+ 7]       ) << 4) | (((uint16_t)a[13*i+ 8] & 0x01) << 12);
    // fallthrough
    case 4:
      r->coeffs[8*i+3] = (a[13*i+ 4] >> 7) | (((uint16_t)a[13*i+ 5]       ) << 1) | (((uint16_t)a[13*i+ 6] & 0x0f) <<  9);
      r->coeffs[8*i+2] = (a[13*i+ 3] >> 2) | (((uint16_t)a[13*i+ 4] & 0x7f) << 6);
    // fallthrough
    case 2:
      r->coeffs[8*i+1] = (a[13*i+ 1] >> 5) | (((uint16_t)a[13*i+ 2]       ) << 3) | (((uint16_t)a[13*i+ 3] & 0x03) << 11);
      r->coeffs[8*i+0] =  a[13*i+ 0]       | (((uint16_t)a[13*i+ 1] & 0x1f) << 8);
  }
  /* Set r[n-1] so that the sum of coefficients is zero mod q */
  r->coeffs[NTRU_N-1] = 0;
  for(i=0;i<NTRU_PACK_DEG;i++)
  {
    r->coeffs[NTRU_N-1] += r->coeffs[i];
  }
  r->coeffs[NTRU_N-1] = MODQ(-(r->coeffs[NTRU_N-1]));
}

void poly_Rq_frommsg(poly *r, const unsigned char *m)
{
  poly b3;
  poly_S3_frombytes(&b3, m);
  poly_S3_to_Rq(r, &b3);
}

void poly_S3_tobytes(unsigned char msg[NTRU_OWCPA_MSGBYTES], const poly *a)
{
  int i;
  unsigned char c;
#if NTRU_PACK_DEG > (NTRU_PACK_DEG / 5) * 5  // if 5 does not divide NTRU_N-1
  int j;
#endif

  for(i=0; i<NTRU_PACK_DEG/5; i++)
  {
    c =        a->coeffs[5*i+4] & 255;
    c = (3*c + a->coeffs[5*i+3]) & 255;
    c = (3*c + a->coeffs[5*i+2]) & 255;
    c = (3*c + a->coeffs[5*i+1]) & 255;
    c = (3*c + a->coeffs[5*i+0]) & 255;
    msg[i] = c;
  }
#if NTRU_PACK_DEG > (NTRU_PACK_DEG / 5) * 5  // if 5 does not divide NTRU_N-1
  i = NTRU_PACK_DEG/5;
  c = 0;
  for(j = NTRU_PACK_DEG - (5*i) - 1; j>=0; j--)
    c = (3*c + a->coeffs[5*i+j]) & 255;
  msg[i] = c;
#endif
}

void poly_S3_tomsg(unsigned char msg[NTRU_OWCPA_MSGBYTES], const poly *a)
{
  poly_S3_tobytes(msg, a);
}


void poly_S3_frombytes(poly *r, const unsigned char msg[NTRU_OWCPA_MSGBYTES])
{
  int i;
  unsigned char c;
#if NTRU_PACK_DEG > (NTRU_PACK_DEG / 5) * 5  // if 5 does not divide NTRU_N-1
  int j;
#endif

  for(i=0; i<NTRU_PACK_DEG/5; i++)
  {
    c = msg[i];
    r->coeffs[5*i+0] = mod3(c);
    r->coeffs[5*i+1] = mod3(c * 171 >> 9);  // this is division by 3
    r->coeffs[5*i+2] = mod3(c * 57 >> 9);  // division by 3^2
    r->coeffs[5*i+3] = mod3(c * 19 >> 9);  // division by 3^3
    r->coeffs[5*i+4] = mod3(c * 203 >> 14);  // etc.
  }
#if NTRU_PACK_DEG > (NTRU_PACK_DEG / 5) * 5  // if 5 does not divide NTRU_N-1
  i = NTRU_PACK_DEG/5;
  c = msg[i];
  for(j=0; (5*i+j)<NTRU_PACK_DEG; j++)
  {
    r->coeffs[5*i+j] = mod3(c);
    c = c * 171 >> 9;
  }
#endif
  r->coeffs[NTRU_N-1] = 0;
}

void poly_S3_sample(poly *r, const unsigned char *seed, const unsigned char nonce)
{
  uint32_t buf[(NTRU_N+7)/8];
  unsigned char extseed[NTRU_SEEDBYTES+8];
  int i;

  for(i=0;i<NTRU_SEEDBYTES;i++)
    extseed[i] = seed[i];
  for(i=1;i<8;i++)
    extseed[NTRU_SEEDBYTES+i] = 0;
  extseed[NTRU_SEEDBYTES] = nonce;

  shake128((unsigned char *)buf, sizeof(buf), extseed, sizeof(extseed));

  cbdS3(r, buf);
}

void poly_S3_sample_plus(poly *r, const unsigned char *seed, const unsigned char nonce)
{
  /* Samples r(X) then checks sign of inner product between
   * r(X) and X*r(X). If negative, flips sign of every second
   * coefficient of r(X).
   * Assumes r(X) has coeffs in {0,1,2}.
   * Treats r(X) as {-1,0,1} vector in ZZ^n.
   */
  int i;
  uint16_t c = 0;
  uint16_t s = 0;

  poly_S3_sample(r, seed, nonce);

  for(i=0; i<NTRU_N-1; i++)
  {
    c = r->coeffs[i] * r->coeffs[i+1];
    s += ZP_PROD_TO_UINT16(c);
  }
  /* Map sign of correlation to element of Zp.     */
  s = ((s >> 15) & 1) + 1; /* s = (s >= 0) ? 1 : 2 */

  for(i=0; i<NTRU_N; i+=2)
    r->coeffs[i] = mod3(r->coeffs[i]*s);
}

void poly_Rq_getnoise(poly *r, const unsigned char *seed, const unsigned char nonce)
{
  int i;

  poly_S3_sample(r, seed, nonce);
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = ZP_TO_ZQ(r->coeffs[i]);
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
