#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* pk = (unsigned char*) malloc(CRYPTO_PUBLICKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);
    int rv = 0;

    size_t pk_bytes = fread(pk, 1, CRYPTO_PUBLICKEYBYTES, stdin);
    if(pk_bytes != CRYPTO_PUBLICKEYBYTES) {
      fprintf(stderr, "Read error.\n");
      rv = -1;
      goto cleanup;
    }

    crypto_kem_enc(c, k, pk);

    size_t ct_bytes = fwrite(c, 1, CRYPTO_CIPHERTEXTBYTES, stdout);
    if(ct_bytes != CRYPTO_CIPHERTEXTBYTES) {
      fprintf(stderr, "Write error.\n");
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
    free(pk);
    free(c);
    free(k);

    return rv;
}
