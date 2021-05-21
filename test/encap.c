#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* pk = (unsigned char*) malloc(CRYPTO_PUBLICKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);

    size_t pk_bytes = fread(pk, 1, CRYPTO_PUBLICKEYBYTES, stdin);

    if (pk_bytes != CRYPTO_PUBLICKEYBYTES) {
        fprintf (stderr, "Error occurred while reading.\n");
        fprintf (stderr,  "Read %ld bytes for public key.\n", pk_bytes);

        free (pk);
        free (c);
        free (k);
        
        exit (-1);
    }

    crypto_kem_enc(c, k, pk);

    fwrite(c, 1, CRYPTO_CIPHERTEXTBYTES, stdout);
    fwrite(k, 1, CRYPTO_BYTES, stdout);

    fclose(stdout);

    free(pk);
    free(c);
    free(k);

    return 0;
}
