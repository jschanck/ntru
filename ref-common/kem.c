#include "api.h"
#include "cmov.h"
#include "crypto_hash_sha3256.h"
#include "kem.h"
#include "owcpa.h"
#include "params.h"
#include "randombytes.h"
#include "sample.h"

// API FUNCTIONS 
int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
  unsigned char seed[NTRU_SAMPLE_FG_BYTES];

  randombytes(seed, NTRU_SAMPLE_FG_BYTES);
  owcpa_keypair(pk, sk, seed);

  randombytes(sk+NTRU_OWCPA_SECRETKEYBYTES, NTRU_PRFKEYBYTES);

  return 0;
}

int crypto_kem_enc(unsigned char *c, unsigned char *k, const unsigned char *pk)
{
  poly r, m;
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  unsigned char rm_seed[NTRU_SAMPLE_RM_BYTES];

  randombytes(rm_seed, NTRU_SAMPLE_RM_BYTES);

  sample_rm(&r, &m, rm_seed);

  poly_S3_tobytes(rm, &r);
  poly_S3_tobytes(rm+NTRU_PACK_TRINARY_BYTES, &m);
  crypto_hash_sha3256(k, rm, NTRU_OWCPA_MSGBYTES);

  poly_Z3_to_Zq(&r);
  owcpa_enc(c, &r, &m, pk);

  return 0;
}

int crypto_kem_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk)
{
  int i, fail;
  unsigned char rm[NTRU_OWCPA_MSGBYTES];
  unsigned char buf[NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES];

  fail = owcpa_dec(rm, c, sk);
  /* If fail = 0 then c = Enc(h, rm). There is no need to re-encapsulate. */
  /* See comment in owcpa_dec for details.                                */

  crypto_hash_sha3256(k, rm, NTRU_OWCPA_MSGBYTES);

  /* shake(secret PRF key || input ciphertext) */
  for(i=0;i<NTRU_PRFKEYBYTES;i++)
    buf[i] = sk[i+NTRU_OWCPA_SECRETKEYBYTES];
  for(i=0;i<NTRU_CIPHERTEXTBYTES;i++)
    buf[NTRU_PRFKEYBYTES + i] = c[i];
  crypto_hash_sha3256(rm, buf, NTRU_PRFKEYBYTES+NTRU_CIPHERTEXTBYTES);

  cmov(k, rm, NTRU_SHAREDKEYBYTES, (unsigned char) fail);

  return 0;
}
