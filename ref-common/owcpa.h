#ifndef OWCPA_H
#define OWCPA_H

#include "params.h"
#include "poly.h"

#define owcpa_keypair CRYPTO_NAMESPACE(owcpa_keypair)
void owcpa_keypair(unsigned char *pk,
                   unsigned char *sk,
                   const unsigned char seed[NTRU_SAMPLE_FG_BYTES]);

#define owcpa_enc CRYPTO_NAMESPACE(owcpa_enc)
void owcpa_enc(unsigned char *c,
               const poly *r,
               const poly *m,
               const unsigned char *pk);

#define owcpa_dec CRYPTO_NAMESPACE(owcpa_dec)
int owcpa_dec(unsigned char *rm,
              const unsigned char *ciphertext,
              const unsigned char *secretkey);
#endif
