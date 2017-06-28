#include <stdlib.h>
#include <stdio.h>
#include "../params.h"
#include "../ntrukem.h"
#include "../verify.h"

#define TRIALS 100
int main(void)
{
  int i,c;
  unsigned char* pk = (unsigned char*) malloc(NTRU_PUBLICKEYBYTES);
  unsigned char* sk = (unsigned char*) malloc(NTRU_SECRETKEYBYTES);
  unsigned char* ct = (unsigned char*) malloc(NTRU_BYTES);
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
