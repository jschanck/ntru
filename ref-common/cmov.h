#ifndef VERIFY_H
#define VERIFY_H

#include "params.h"

#include <stddef.h>

#define cmov CRYPTO_NAMESPACE(cmov)
void cmov(unsigned char *r, const unsigned char *x, size_t len, unsigned char b);

#endif
