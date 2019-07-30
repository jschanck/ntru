#define int32_MINMAX(a,b) \
do { \
  int32 temp1; \
  asm( \
    "cmpl %1,%0\n\t" \
    "mov %0,%2\n\t" \
    "cmovg %1,%0\n\t" \
    "cmovg %2,%1\n\t" \
    : "+r"(a), "+r"(b), "=r"(temp1) \
    : \
    : "cc" \
  ); \
} while(0)
