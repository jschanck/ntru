#include "sample.h"
#include "crypto_sort.h"
#include "fips202.h"

void sample_xof(unsigned char *output, const size_t sizeof_output, const unsigned char seed[NTRU_SEEDBYTES])
{
  shake128(output, sizeof_output, seed, NTRU_SEEDBYTES);
}

void sample_fg(poly *f, poly *g, const unsigned char uniformbytes[NTRU_SAMPLE_FG_BYTES])
{
  sample_iid(f,uniformbytes);
  sample_fixed_type(g,uniformbytes+NTRU_SAMPLE_IID_BYTES);
}

void sample_rm(poly *r, poly *m, const unsigned char uniformbytes[NTRU_SAMPLE_RM_BYTES])
{
  sample_iid(r,uniformbytes);
  sample_fixed_type(m,uniformbytes+NTRU_SAMPLE_IID_BYTES);
}

void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES])
{
  int i;
  /* {0,1,...,255} -> {0,1,2}; Pr[0] = 86/256, Pr[1] = Pr[-1] = 85/256 */
  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = mod3(uniformbytes[i]);

  r->coeffs[NTRU_N-1] = 0;
}

void sample_fixed_type(poly *r, const unsigned char u[NTRU_SAMPLE_FT_BYTES])
{
  // XXX: Assumes NTRU_SAMPLE_FT_BYTES = 4*N - 4.

  int32_t s[NTRU_N-1];
  int i;

  for (i = 0; i < NTRU_N-1; i++)
    s[i] = u[4*i+0] + (u[4*i+1] << 8) + (u[4*i+2] << 16) + (u[4*i+3] << 24);

  for (i = 0; i<NTRU_N-1; i++) s[i] &= -4;

  for (i = 0; i<NTRU_WEIGHT/2; i++) s[i] |=  1;

  for (i = NTRU_WEIGHT/2; i<NTRU_WEIGHT; i++) s[i] |=  2;

  crypto_sort(s,NTRU_N-1);

  for(i=0; i<NTRU_N-1; i++)
    r->coeffs[i] = ((uint16_t) (s[i] & 3));

  r->coeffs[NTRU_N-1] = 0;
}
