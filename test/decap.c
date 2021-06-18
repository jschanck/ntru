#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* sk = (unsigned char*) malloc(CRYPTO_SECRETKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);
    int rv = 0;

    size_t sk_bytes = fread(sk, 1, CRYPTO_SECRETKEYBYTES, stdin);
    if(sk_bytes != CRYPTO_SECRETKEYBYTES) {
      fprintf(stderr, "Read error.\n");
      rv = -1;
      goto cleanup;
    }

    size_t ct_bytes = fread(c, 1, CRYPTO_CIPHERTEXTBYTES, stdin);
    if(ct_bytes != CRYPTO_CIPHERTEXTBYTES) {
      fprintf(stderr, "Read error.\n");
      rv = -1;
      goto cleanup;
    }

    int dec_fail = crypto_kem_dec(k, c, sk);
    if(dec_fail) {
      rv = -1;
      goto cleanup;
    }

    size_t k_bytes = fwrite(k, 1, CRYPTO_BYTES, stdout);
    if(k_bytes != CRYPTO_BYTES) {
      fprintf(stderr, "Write error.\n");
      rv = -1;
      goto cleanup;
    }

cleanup:
    free(sk);
    free(c);
    free(k);

    return rv;
}
