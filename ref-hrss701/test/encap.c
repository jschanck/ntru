#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* pk = (unsigned char*) malloc(CRYPTO_PUBLICKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);

    fread(pk, 1, CRYPTO_PUBLICKEYBYTES, stdin);

    crypto_kem_enc(c, k, pk);

    fwrite(c, 1, CRYPTO_CIPHERTEXTBYTES, stdout);
    fwrite(k, 1, CRYPTO_BYTES, stdout);

    fclose(stdout);

    free(pk);
    free(c);
    free(k);

    return 0;
}
