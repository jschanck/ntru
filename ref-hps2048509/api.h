#ifndef API_H
#define API_H

#define CRYPTO_SECRETKEYBYTES 935
#define CRYPTO_PUBLICKEYBYTES 699
#define CRYPTO_CIPHERTEXTBYTES 699
#define CRYPTO_BYTES 32

#define CRYPTO_ALGNAME "ntruhps2048509"

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk);

int crypto_kem_enc(unsigned char *c, unsigned char *k, const unsigned char *pk);

int crypto_kem_dec(unsigned char *k, const unsigned char *c, const unsigned char *sk);

#endif
