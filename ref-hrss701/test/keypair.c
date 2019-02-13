#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* pk = (unsigned char*) malloc(CRYPTO_PUBLICKEYBYTES);
    unsigned char* sk = (unsigned char*) malloc(CRYPTO_SECRETKEYBYTES);

    crypto_kem_keypair(pk, sk);

    fwrite(pk, 1, CRYPTO_PUBLICKEYBYTES, stdout);
    fwrite(sk, 1, CRYPTO_SECRETKEYBYTES, stdout);

    fclose(stdout);

    free(sk);
    free(pk);

    return 0;
}
