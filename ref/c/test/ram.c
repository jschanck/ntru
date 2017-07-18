#include "../ntrukem.h"
#include "../params.h"
#include "../cpucycles.h"
#include "../randombytes.h"
#include "../poly.h"
#include <stdlib.h>
#include <stdio.h>

#define MAXMEASURE 4194304

int main()
{
  unsigned char* pks = (unsigned char*) malloc(NTRU_PUBLICKEYBYTES);
  unsigned char* sks = (unsigned char*) malloc(NTRU_SECRETKEYBYTES);
  unsigned char* cts = (unsigned char*) malloc(NTRU_CIPHERTEXTBYTES);
  unsigned char* k1 = (unsigned char*) malloc(NTRU_SHAREDKEYBYTES);
  unsigned char* k2 = (unsigned char*) malloc(NTRU_SHAREDKEYBYTES);

  int i;
  unsigned char volatile canary;

  for (i = 0; i < MAXMEASURE; i++) {
    *(&canary - i) = 0x42;
  }

  crypto_kem_keypair(pks, sks);
  crypto_kem_enc(cts, k1, pks);
  crypto_kem_dec(k2, cts, sks);

  for (i = MAXMEASURE-1; i >= 0; i--) {
    if (*(&canary - i) != 0x42) {
      printf("Canary broken at %d\n", i);
      break;
    }
  }

  free(pks);
  free(sks);
  free(cts);
  free(k1);
  free(k2);

  return 0;
}
