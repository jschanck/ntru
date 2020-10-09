#include "../crypto_hash_sha3256.h"
#include "../kem.h"
#include "../owcpa.h"
#include "../params.h"

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

  unsigned char pk[NTRU_PUBLICKEYBYTES];
  unsigned char sk[NTRU_SECRETKEYBYTES];
  unsigned char ct[NTRU_CIPHERTEXTBYTES];
  unsigned char k1[NTRU_SHAREDKEYBYTES];
  unsigned char k2[NTRU_SHAREDKEYBYTES];

  unsigned char buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES];
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  poly r, m;

  crypto_kem_keypair(pk, sk);
  crypto_kem_enc(ct, k1, pk);

  fail = owcpa_dec(rm, ct, sk);
  assert(fail == 0);

  crypto_hash_sha3256(k2, rm, NTRU_OWCPA_MSGBYTES);
  assert(verify(k1,k2,NTRU_SHAREDKEYBYTES) == 0);

  if(7&(NTRU_LOGQ*NTRU_PACK_DEG))
  {
    /* If there are trailing bits, then test the behavior of owcpa_check_ciphertext. */

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
  for(i=0; i<NTRU_N-1; i++)
  {
    if(m.coeffs[i] == 0)
    {
      m.coeffs[i] = 1;
      break;
    }
  }
  for(i=0; i<NTRU_N-1; i++)
  {
    if(m.coeffs[i] == 0)
    {
      m.coeffs[i] = 2;
      break;
    }
  }
  owcpa_enc(ct, &r, &m, pk);
  assert(owcpa_dec(rm, ct, sk) == 1);
#endif

  printf("success\n");
  return 0;
}
