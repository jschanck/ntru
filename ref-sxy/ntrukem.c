#include "randombytes.h"
#include "fips202.h"
#include "params.h"
#include "verify.h"
#include "owcpa.h"

// API FUNCTIONS 
int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
  unsigned char seed[NTRU_SEEDBYTES];

  randombytes(seed, NTRU_SEEDBYTES);
  owcpa_keypair(pk, sk, seed);

  randombytes(sk+NTRU_OWCPA_SECRETKEYBYTES, NTRU_PRFKEYBYTES);

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
  unsigned char buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES];
  unsigned char *cmp = buf+NTRU_PRFKEYBYTES;

  fail = 0;
  fail |= owcpa_dec_and_reenc(cmp, rm, c, sk);
  fail |= verify(c, cmp, NTRU_CIPHERTEXTBYTES);

  shake128(k, NTRU_SHAREDKEYBYTES, rm, NTRU_OWCPA_MSGBYTES);

  /* shake(secret PRF key || input ciphertext) */
  for(i=0;i<NTRU_PRFKEYBYTES;i++)
    buf[i] = sk[i+NTRU_OWCPA_SECRETKEYBYTES];
  for(i=0;i<NTRU_CIPHERTEXTBYTES;i++)
    cmp[i] = c[i];
  shake128(rm, NTRU_SHAREDKEYBYTES, cmp, NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES);

  cmov(k, rm, NTRU_SHAREDKEYBYTES, fail);

  return fail;
}
