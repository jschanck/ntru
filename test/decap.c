#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* sk = (unsigned char*) malloc(CRYPTO_SECRETKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);
    int result;

    fread(sk, 1, CRYPTO_SECRETKEYBYTES, stdin);
    fread(c, 1, CRYPTO_CIPHERTEXTBYTES, stdin);

    result = crypto_kem_dec(k, c, sk);

    fwrite(k, 1, CRYPTO_BYTES, stdout);

    fclose(stdout);

    free(sk);
    free(c);
    free(k);

    return result;
}
