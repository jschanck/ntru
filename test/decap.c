#include "../api.h"
#include "../kem.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    unsigned char* sk = (unsigned char*) malloc(CRYPTO_SECRETKEYBYTES);
    unsigned char* c = (unsigned char*) malloc(CRYPTO_CIPHERTEXTBYTES);
    unsigned char* k = (unsigned char*) malloc(CRYPTO_BYTES);
    int result;

    size_t sk_bytes = fread(sk, 1, CRYPTO_SECRETKEYBYTES, stdin);
    size_t c_bytes = fread(c, 1, CRYPTO_CIPHERTEXTBYTES, stdin);

    if (sk_bytes != CRYPTO_SECRETKEYBYTES || c_bytes != CRYPTO_CIPHERTEXTBYTES) {
        fprintf (stderr, "Error occurred while reading.\n");
        fprintf (stderr,  "Read %ld bytes for secret key and %ld bytes for ciphertext.\n", sk_bytes, c_bytes);

        free (sk);
        free (c);
        free (k);

        exit (-1);
    }

    result = crypto_kem_dec(k, c, sk);

    fwrite(k, 1, CRYPTO_BYTES, stdout);

    fclose(stdout);

    free(sk);
    free(c);
    free(k);

    return result;
}
