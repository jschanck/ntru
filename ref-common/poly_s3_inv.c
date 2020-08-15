/* Based on supercop-20200702/crypto_core/invhrss701/simpler/core.c */

#include "poly.h"

static inline uint8_t mod3(uint8_t a) /* a between 0 and 9 */
{
  int16_t t, c;
  a = (a >> 2) + (a & 3); /* between 0 and 4 */
  t = a - 3;
  c = t >> 5;
  return t^(c&(a^t));
}

/* return -1 if x<0 and y<0; otherwise return 0 */
static inline int both_negative_mask(int x,int y)
{
  return (x & y) >> 15;
}

void poly_S3_inv(poly *out, const poly *in)
{
  poly f, g, v, r;
  int i,loop,delta;
  int sign,swap,t;

  for (i = 0;i < NTRU_N;++i) v.coeffs[i] = 0;
  for (i = 0;i < NTRU_N;++i) r.coeffs[i] = 0;
  r.coeffs[0] = 1;

  for (i = 0;i < NTRU_N;++i) f.coeffs[i] = 1;
  for (i = 0;i < NTRU_N-1;++i) g.coeffs[NTRU_N-2-i] = mod3((in->coeffs[i] & 3) + 2*(in->coeffs[NTRU_N-1] & 3));
  g.coeffs[NTRU_N-1] = 0;

  delta = 1;

  for (loop = 0;loop < 2*(NTRU_N-1)-1;++loop) {
    for (i = NTRU_N-1;i > 0;--i) v.coeffs[i] = v.coeffs[i-1];
    v.coeffs[0] = 0;

    sign = mod3(2 * g.coeffs[0] * f.coeffs[0]);
    swap = both_negative_mask(-delta,-(int) g.coeffs[0]);
    delta ^= swap & (delta ^ -delta);
    delta += 1;

    for (i = 0;i < NTRU_N;++i) {
      t = swap&(f.coeffs[i]^g.coeffs[i]); f.coeffs[i] ^= t; g.coeffs[i] ^= t;
      t = swap&(v.coeffs[i]^r.coeffs[i]); v.coeffs[i] ^= t; r.coeffs[i] ^= t;
    }

    for (i = 0;i < NTRU_N;++i) g.coeffs[i] = mod3(g.coeffs[i]+sign*f.coeffs[i]);
    for (i = 0;i < NTRU_N;++i) r.coeffs[i] = mod3(r.coeffs[i]+sign*v.coeffs[i]);
    for (i = 0;i < NTRU_N-1;++i) g.coeffs[i] = g.coeffs[i+1];
    g.coeffs[NTRU_N-1] = 0;
  }

  sign = f.coeffs[0];
  for (i = 0;i < NTRU_N-1;++i) out->coeffs[i] = mod3(sign*v.coeffs[NTRU_N-2-i]);
}
