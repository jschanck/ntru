#include "randombytes.h"
#include "fips202.h"
#include "params.h"
#include "verify.h"
#include "owcpa.h"

// API FUNCTIONS 
int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
  owcpa_keypair(pk, sk);
  randombytes(sk+NTRU_OWCPA_SECRETKEYBYTES, NTRU_SEEDBYTES);

  return 0;
}

int crypto_kem_enc(unsigned char *c, unsigned char *k, const unsigned char *pk)
{
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  unsigned char rm_seed[NTRU_SEEDBYTES];

  /* TODO: Should we use a larger seed? Sample r and m independently? */
  randombytes(rm_seed, NTRU_SEEDBYTES);
  owcpa_samplemsg(rm, rm_seed);

  shake128(k, NTRU_SHAREDKEYBYTES, rm, NTRU_OWCPA_MSGBYTES);

  owcpa_enc(c, rm, pk);

  return 0;
}

int crypto_kem_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk)
{
  int i, fail;
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  unsigned char cmp[NTRU_CIPHERTEXTBYTES];

  fail = 0;
  fail |= owcpa_dec_and_reenc(cmp, rm, c, sk);
  fail |= verify(c, cmp, NTRU_CIPHERTEXTBYTES);

  shake128(k, NTRU_SHAREDKEYBYTES, rm, NTRU_OWCPA_MSGBYTES);

  /* TODO: Something nicer here? We need a random output that depends on */
  /* c and the secret domain separator s. I'm just doing shake(s ^ c).   */
  for(i=0;i<NTRU_CIPHERTEXTBYTES;i++)
    cmp[i] = c[i];
  for(i=0;i<NTRU_SHAREDKEYBYTES;i++)
    cmp[i] ^= sk[i+NTRU_OWCPA_SECRETKEYBYTES];
  shake128(rm, NTRU_SHAREDKEYBYTES, cmp, NTRU_CIPHERTEXTBYTES);

  cmov(k, rm, NTRU_SHAREDKEYBYTES, fail);

  return fail;
}
