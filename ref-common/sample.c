#include "sample.h"
#include "fips202.h"

void sample_xof(unsigned char *output, const size_t sizeof_output, const unsigned char seed[NTRU_SEEDBYTES])
{
  shake128(output, sizeof_output, seed, NTRU_SEEDBYTES);
}

void sample_fg(poly *f, poly *g, const unsigned char uniformbytes[NTRU_SAMPLE_FG_BYTES])
{
#ifdef NTRU_HRSS
  sample_iid_plus(f,uniformbytes);
  sample_iid_plus(g,uniformbytes+NTRU_SAMPLE_IID_BYTES);
#endif

#ifdef NTRU_HPS
  sample_iid(f,uniformbytes);
  sample_fixed_type(g,uniformbytes+NTRU_SAMPLE_IID_BYTES);
#endif
}

void sample_rm(poly *r, poly *m, const unsigned char uniformbytes[NTRU_SAMPLE_RM_BYTES])
{
#ifdef NTRU_HRSS
  sample_iid(r,uniformbytes);
  sample_iid(m,uniformbytes+NTRU_SAMPLE_IID_BYTES);
#endif

#ifdef NTRU_HPS
  sample_iid(r,uniformbytes);
  sample_fixed_type(m,uniformbytes+NTRU_SAMPLE_IID_BYTES);
#endif
}

void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES])
{
  int i;
  /* {0,1,...,255} -> {0,1,2}; Pr[0] = 86/256, Pr[1] = Pr[-1] = 85/256 */
  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = mod3(uniformbytes[i]);

  r->coeffs[NTRU_N-1] = 0;
}

#ifdef NTRU_HRSS
void sample_iid_plus(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES])
{
  /* Sample r using sample_iid then conditionally flip    */
  /* signs of even index coefficients so that <x*r, r> >= 0.      */

  int i;
  uint16_t s = 0;

  sample_iid(r, uniformbytes);

  /* Map {0,1,2} -> {0, 1, 2^16 - 1} */
  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = r->coeffs[i] | (-(r->coeffs[i]>>1));

  /* s = <x*r, r>.  (r[n-1] = 0) */
  for(i=0; i<NTRU_N-1; i++)
    s += r->coeffs[i+1] * r->coeffs[i];

  /* Extract sign of s (sign(0) = 1) */
  s = 1 | (-(s>>15));

  for(i=0; i<NTRU_N; i+=2)
    r->coeffs[i] = s * r->coeffs[i];

  /* Map {0,1,2^16-1} -> {0, 1, 2} */
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = 3 & (r->coeffs[i] ^ (r->coeffs[i]>>15));
}
#endif

#ifdef NTRU_HPS
#include "crypto_sort.h"
void sample_fixed_type(poly *r, const unsigned char u[NTRU_SAMPLE_FT_BYTES])
{
  // XXX: Assumes NTRU_SAMPLE_FT_BYTES = 4*N - 4.

  int32_t s[NTRU_N-1];
  int i;

  for (i = 0; i < NTRU_N-1; i++)
  {
    s[i] = u[4*i+0] + (u[4*i+1] << 8) + (u[4*i+2] << 16) + (u[4*i+3] << 24);
    s[i] &= -4;
  }

  for (i = 0; i<NTRU_WEIGHT/2; i++) s[i] |=  1;

  for (i = NTRU_WEIGHT/2; i<NTRU_WEIGHT; i++) s[i] |=  2;

  crypto_sort(s,NTRU_N-1);

  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = ((uint16_t) (s[i] & 3));

  r->coeffs[NTRU_N-1] = 0;
}
#endif
