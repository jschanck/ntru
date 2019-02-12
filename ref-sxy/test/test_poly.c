#include <stdio.h>
#include <stdint.h>
#include "../poly.h"
#include "../randombytes.h"

static void poly_S3_a_dot_xa_count(int *pos, int *neg, int *zero, const poly *a)
{
  int i;
  *pos = 0;
  *neg = 0;
  *zero = 0;
  for(i=0; i<NTRU_N-1; i++)
    switch(a->coeffs[i] * a->coeffs[i+1])
    {
      case 0:
        *zero += 1;
        break;
      case 1:
      case 4:
        *pos += 1;
        break;
      case 2:
        *neg += 1;
        break;
    }
}


static int test_sample_plus(const unsigned char seed[NTRU_SEEDBYTES], const unsigned char nonce)
{
  int i;
  poly a;
  poly b;
  int pos_a, neg_a, zero_a;
  int pos_b, neg_b, zero_b;

  unsigned char uniformbytes[NTRU_S3_RANDOMBYTES];
  unsigned char domain[NTRU_DOMAINBYTES] = {0};
  domain[0] = nonce;

  poly_S3_xof(uniformbytes, sizeof(uniformbytes), seed, domain);

  poly_S3_format(&a, uniformbytes);
  poly_S3_a_dot_xa_count(&pos_a, &neg_a, &zero_a, &a);

  poly_S3_format_plus(&b, uniformbytes);
  poly_S3_a_dot_xa_count(&pos_b, &neg_b, &zero_b, &b);

  /* Total count should be N-1 */
  if((pos_a + neg_a + zero_a) != NTRU_N-1)
    return -1;
  if((pos_b + neg_b + zero_b) != NTRU_N-1)
    return -1;

  /* Number of zeros should never change */
  if(zero_a - zero_b)
    return -1;

  /* Odd index coefficents should be unchanged */
  for(i=1; i<NTRU_N; i+=2)
    if(a.coeffs[i] != b.coeffs[i])
      return -1;

  if(neg_a > pos_a)
  { /* Signs should have flipped */
    if((pos_a - neg_b) || (neg_a - pos_b))
      return -1;
  }
  else
  { /* All coeffs should be the same */
    for(i=0; i<NTRU_N; i++)
      if(a.coeffs[i] != b.coeffs[i])
        return -1;
  }

  return 0;
}

static int test_all_sample_plus_cases()
{
  poly a;
  int pos_a, neg_a, zero_a;
  unsigned char seed[NTRU_SEEDBYTES] = {0};
  unsigned char domain[NTRU_DOMAINBYTES] = {0};
  unsigned char uniformbytes[NTRU_S3_RANDOMBYTES];

  seed[0] = 3;
  domain[0] = 1;

  poly_S3_xof(uniformbytes, sizeof(uniformbytes), seed, domain);

  /* For seed 3, domain 1 has positive correlation */
  poly_S3_format(&a, uniformbytes);
  poly_S3_a_dot_xa_count(&pos_a, &neg_a, &zero_a, &a);
  if(!(pos_a > neg_a))
    return -1;

  /* domain 3 has negative correlation */
  domain[0] = 3;
  poly_S3_xof(uniformbytes, sizeof(uniformbytes), seed, domain);
  poly_S3_format(&a, uniformbytes);
  poly_S3_a_dot_xa_count(&pos_a, &neg_a, &zero_a, &a);
  if(!(pos_a < neg_a))
    return -1;

  /* domain 12 has zero correlation*/
  domain[0] = 12;
  poly_S3_xof(uniformbytes, sizeof(uniformbytes), seed, domain);
  poly_S3_format(&a, uniformbytes);
  poly_S3_a_dot_xa_count(&pos_a, &neg_a, &zero_a, &a);
  if(!(pos_a == neg_a))
    return -1;

  if(test_sample_plus(seed, 1) ||
     test_sample_plus(seed, 3) ||
     test_sample_plus(seed, 12))
    return -1;

  return 0;
}

int main(void)
{
  printf("TEST_SAMPLE_PLUS:\t%d\n", test_all_sample_plus_cases());
  return 0;
}
