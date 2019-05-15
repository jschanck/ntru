#include <stdint.h>
#include "crypto_sort.h"
#include "djbsort/int32_sort.h"

// The avx2 version of djbsort (version 20180729) is used for sorting.
// The source can be found at https://sorting.cr.yp.to/
void crypto_sort(void *array,long long n)
{
  int32_sort(array, n);
}
