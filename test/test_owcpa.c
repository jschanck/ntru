#include "../crypto_hash_sha3256.h"
#include "../kem.h"
#include "../owcpa.h"
#include "../params.h"
#include "../randombytes.h"
#include "../sample.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* returns 0 for equal strings, 1 for non-equal strings */
static unsigned char verify(const unsigned char *a, const unsigned char *b, size_t len)
{
  uint64_t r;
  size_t i;

  r = 0;
  for(i=0;i<len;i++)
    r |= a[i] ^ b[i];

  r = (~r + 1); // Two's complement
  r >>= 63;
  return (unsigned char)r;
}

int main(void)
{
  int i, inc, fail;
  int16_t g1;

  unsigned char pk[NTRU_PUBLICKEYBYTES];
  unsigned char sk[NTRU_SECRETKEYBYTES];
  unsigned char ct[NTRU_CIPHERTEXTBYTES];
  unsigned char k1[NTRU_SHAREDKEYBYTES];
  unsigned char k2[NTRU_SHAREDKEYBYTES];

  unsigned char buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES];

  unsigned char rm_seed[NTRU_SAMPLE_RM_BYTES];
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  poly h, f, fp, g, r, m, x1, x2;

  crypto_kem_keypair(pk, sk);

  /* Test that f and fp are inversed mod p */
  poly_S3_frombytes(&f, sk);
  poly_S3_frombytes(&fp, sk+NTRU_PACK_TRINARY_BYTES);
  poly_S3_mul(&x1, &f, &fp);
  assert(x1.coeffs[0] == 1);
  for(i=1; i<NTRU_N; i++)
    assert(x1.coeffs[i] == 0);

  /* Test that the public key satisfies h*f = 3*g for g of the right form */
  poly_Rq_sum_zero_frombytes(&h, pk);
  poly_S3_frombytes(&f, sk);
  poly_Z3_to_Zq(&f);
  poly_Rq_mul(&g, &h, &f);
  if(NTRU_Q % 3 == 1) for(i=0; i<NTRU_N; i++) g.coeffs[i] *= -(NTRU_Q-1)/3;
  if(NTRU_Q % 3 == 2) for(i=0; i<NTRU_N; i++) g.coeffs[i] *= (NTRU_Q+1)/3;
  for(i=0; i<NTRU_N; i++) g.coeffs[i] &= (NTRU_Q-1);

#ifdef NTRU_HRSS
  /* Check that g has coeffs in {-2,-1,0,1,2}. */
  for(i=0; i<NTRU_N; i++) assert(((g.coeffs[i]+2) & (NTRU_Q-1)) < 5);

  /* Check that g satisfies g(1) = 0 (mod q) */ 
  g1 = 0; for(i=0; i<NTRU_N; i++) g1 += g.coeffs[i];
  assert((g1&(NTRU_Q-1)) == 0);
#endif

#ifdef NTRU_HPS
  /* Check that g has coeffs in {-1,0,1} */
  for(i=0; i<NTRU_N; i++) assert(((g.coeffs[i]+1) & (NTRU_Q-1)) < 3);

  /* Check that g has the correct number of +1s */
  g1 = 0; for(i=0; i<NTRU_N; i++) if(g.coeffs[i] == 1) g1++;
  assert(g1 == NTRU_Q/16 - 1);

  /* Check that g has the correct number of -1s */
  g1 = 0; for(i=0; i<NTRU_N; i++) if(g.coeffs[i] == NTRU_Q-1) g1++;
  assert(g1 == NTRU_Q/16 - 1);

  /* note: correct weight implies g(1) = 0 */
#endif

  /* test encaps/decaps */
  randombytes(rm_seed, NTRU_SAMPLE_RM_BYTES);
  sample_rm(&r, &m, rm_seed);
  poly_Z3_to_Zq(&r);
  owcpa_enc(ct, &r, &m, pk);
  fail = owcpa_dec(rm, ct, sk);
  /* Should return 0 on success */
  assert(fail == 0);

  /* output should match input */
  poly_S3_frombytes(&x1, rm);
  poly_Z3_to_Zq(&x1);
  poly_S3_frombytes(&x2, rm+NTRU_PACK_TRINARY_BYTES);
  for(i=0; i<NTRU_N; i++)
  {
    assert(r.coeffs[i] == x1.coeffs[i]);
    assert(m.coeffs[i] == x2.coeffs[i]);
  }

  /* Test owcpa_check_ciphertext. */
  if(7&(NTRU_LOGQ*NTRU_PACK_DEG))
  {
    /* We construct "prf key | ct" in a new buffer, manipulate the last byte of
     * the ct component, and then check that crypto_kem_dec outputs H(prf key | ct).
     * We also check that owcpa_dec outputs 1.
     */
    for(i=0;i<NTRU_PRFKEYBYTES;i++)
      buf[i] = sk[i+NTRU_OWCPA_SECRETKEYBYTES];
    for(i=0;i<NTRU_CIPHERTEXTBYTES;i++)
      buf[NTRU_PRFKEYBYTES + i] = ct[i];

    /* invalid values of the last byte differ by multiples of inc */
    inc = 1 << (7 & (NTRU_LOGQ*NTRU_PACK_DEG));
    while(buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES-1] + inc < 256)
    {
      buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES-1] += inc;

      /* owcpa_check_ciphertext should fail */
      fail = owcpa_dec(rm, buf+NTRU_PRFKEYBYTES, sk);
      assert(fail == 1);

      /* crypto_kem_dec should return the H(prf key | ct) */
      crypto_hash_sha3256(k1, buf, NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES);
      crypto_kem_dec(k2, buf+NTRU_PRFKEYBYTES, sk);

      assert(verify(k1,k2,NTRU_SHAREDKEYBYTES) == 0);
    }
  }

  /* Test the behavior of owcpa_check_r */
  poly_S3_frombytes(&r, rm);
  poly_S3_frombytes(&m, rm+NTRU_PACK_TRINARY_BYTES);

  /* Must not have any values outside of {-1,0,1} */
  for(i=0; i<NTRU_N-1; i++)
  {
    r.coeffs[i] = 2;
    owcpa_enc(ct, &r, &m, pk);
    assert(owcpa_dec(rm, ct, sk) == 1);
    r.coeffs[i] = 0;

    r.coeffs[i] = NTRU_Q-2;
    owcpa_enc(ct, &r, &m, pk);
    assert(owcpa_dec(rm, ct, sk) == 1);
    r.coeffs[i] = 0;
  }

#ifdef NTRU_HPS
  /* Test the behavior of owcpa_check_m */

  /* Wrong number of -1s */
  for(i=0; i<NTRU_N-1; i++)
  {
    m.coeffs[i] = 2;
  }
  owcpa_enc(ct, &r, &m, pk);
  assert(owcpa_dec(rm, ct, sk) == 1);

  /* Wrong number of +1s */
  for(i=0; i<NTRU_N-1; i++)
  {
    m.coeffs[i] = 1;
  }
  owcpa_enc(ct, &r, &m, pk);
  assert(owcpa_dec(rm, ct, sk) == 1);

  /* Wrong weight, but equal numbers of 1s and -1s */
  poly_S3_frombytes(&m, rm+NTRU_PACK_TRINARY_BYTES);
  i = 0;
  while(i < NTRU_N && m.coeffs[i] != 0) i++;
  m.coeffs[i] = 1;

  i = 0;
  while(i < NTRU_N && m.coeffs[i] != 0) i++;
  m.coeffs[i] = 2;

  owcpa_enc(ct, &r, &m, pk);
  assert(owcpa_dec(rm, ct, sk) == 1);
#endif

  printf("success\n\n");
  return 0;
}
