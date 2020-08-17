#ifndef API_H
#define API_H

#define CRYPTO_SECRETKEYBYTES 1590
#define CRYPTO_PUBLICKEYBYTES 1230
#define CRYPTO_CIPHERTEXTBYTES 1230
#define CRYPTO_BYTES 32

#define CRYPTO_ALGNAME "ntruhps4096821"

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk);

int crypto_kem_enc(unsigned char *c, unsigned char *k, const unsigned char *pk);

int crypto_kem_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk);

#endif
