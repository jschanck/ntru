#ifndef int32_sort_H
#define int32_sort_H

#include <stdint.h>

#define int32_sort djbsort_int32
#define int32_sort_implementation djbsort_int32_implementation
#define int32_sort_version djbsort_int32_version
#define int32_sort_compiler djbsort_int32_compiler

#ifdef __cplusplus
extern "C" {
#endif

extern void int32_sort(int32_t *,long long) __attribute__((visibility("default")));

extern const char int32_sort_implementation[] __attribute__((visibility("default")));
extern const char int32_sort_version[] __attribute__((visibility("default")));
extern const char int32_sort_compiler[] __attribute__((visibility("default")));

#ifdef __cplusplus
}
#endif

#endif
