#ifndef CRYPTO_SORT
#define CRYPTO_SORT

#include "params.h"

#include <stddef.h>
#include <stdint.h>

#define crypto_sort_int32 CRYPTO_NAMESPACE(crypto_sort_int32)
void crypto_sort_int32(int32_t *array,size_t n);

#endif
