#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>

#include "../params.h"
#include "../kem.h"

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

#define TRIALS 100
int main(void)
{
  int i,c;
  unsigned char* pk = (unsigned char*) malloc(NTRU_PUBLICKEYBYTES);
  unsigned char* sk = (unsigned char*) malloc(NTRU_SECRETKEYBYTES);
  unsigned char* ct = (unsigned char*) malloc(NTRU_CIPHERTEXTBYTES);
  unsigned char* k1 = (unsigned char*) malloc(NTRU_SHAREDKEYBYTES);
  unsigned char* k2 = (unsigned char*) malloc(NTRU_SHAREDKEYBYTES);

  crypto_kem_keypair(pk, sk);

  c = 0;
  for(i=0; i<TRIALS; i++)
  {
    crypto_kem_enc(ct, k1, pk);
    crypto_kem_dec(k2, ct, sk);
    c += verify(k1, k2, NTRU_SHAREDKEYBYTES);
  }
  printf("ERRORS: %d/%d\n\n", c, TRIALS);

  free(sk);
  free(pk);
  free(ct);
  free(k1);
  free(k2);

  return 0;
}
