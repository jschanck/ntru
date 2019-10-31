#include "../kem.h"
#include "../sample.h"
#include "../params.h"
#include "../cpucycles.h"
#include "../randombytes.h"
#include "../poly_r2_inv.h"
#include <stdlib.h>
#include <stdio.h>

#define NTESTS 100

static int cmp_llu(const void *a, const void*b)
{
  if(*(unsigned long long *)a < *(unsigned long long *)b) return -1;
  if(*(unsigned long long *)a > *(unsigned long long *)b) return 1;
  return 0;
}

static unsigned long long median(unsigned long long *l, size_t llen)
{
  qsort(l,llen,sizeof(unsigned long long),cmp_llu);

  if(llen%2) return l[llen/2];
  else return (l[llen/2-1]+l[llen/2])/2;
}

static unsigned long long average(unsigned long long *t, size_t tlen)
{
  unsigned long long acc=0;
  size_t i;
  for(i=0;i<tlen;i++)
    acc += t[i];
  return acc/(tlen);
}

static void print_results(const char *s, unsigned long long *t, size_t tlen)
{
  size_t i;
  printf("%s", s);
  for(i=0;i<tlen-1;i++)
  {
    t[i] = t[i+1] - t[i];
  //  printf("%llu ", t[i]);
  }
  printf("\n");
  printf("median: %llu\n", median(t, tlen));
  printf("average: %llu\n", average(t, tlen-1));
  printf("\n");
}

static void measure_squaring(unsigned long long *t, const char *label,
                             void (*f)(unsigned char*, const unsigned char*),
                             unsigned char* r, const unsigned char *a)
{
  int i;
  for(i=0; i<NTESTS; i++) {
    t[i] = cpucycles();
    f(r, a);
  }
  print_results(label, t, NTESTS);
}

int main()
{
  poly r, a, b;
  unsigned char a_bytes[(((NTRU_N / 8) + 31) / 32) * 32] __attribute__((aligned(32)));
  unsigned char b_bytes[(((NTRU_N / 8) + 31) / 32) * 32] __attribute__((aligned(32)));
  unsigned char r_bytes[(((NTRU_N / 8) + 31) / 32) * 32] __attribute__((aligned(32)));
  unsigned char uniformbytes[2*NTRU_SAMPLE_IID_BYTES];
  unsigned long long t[NTESTS];
  int i;

  printf("-- inversion in R2 --\n\n");

  randombytes(uniformbytes, sizeof(uniformbytes));
  sample_iid(&a, uniformbytes);
  poly_Z3_to_Zq(&a);
  sample_iid(&b, uniformbytes+NTRU_SAMPLE_IID_BYTES);

  poly_R2_tobytes(a_bytes, &a);
  poly_R2_tobytes(b_bytes, &b);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_R2_mul(r_bytes, a_bytes, b_bytes);
  }
  print_results("poly_R2_mul: ", t, NTESTS);

  measure_squaring(t, "square_1_677: ",   square_1_677,   r_bytes, a_bytes);
  measure_squaring(t, "square_2_677: ",   square_2_677,   r_bytes, a_bytes);
  measure_squaring(t, "square_3_677: ",   square_3_677,   r_bytes, a_bytes);
  measure_squaring(t, "square_5_677: ",   square_5_677,   r_bytes, a_bytes);
  measure_squaring(t, "square_10_677: ",  square_10_677,   r_bytes, a_bytes);
  measure_squaring(t, "square_21_677: ",  square_21_677,  r_bytes, a_bytes);
  measure_squaring(t, "square_42_677: ",  square_42_677,  r_bytes, a_bytes);
  measure_squaring(t, "square_84_677: ",  square_84_677,  r_bytes, a_bytes);
  measure_squaring(t, "square_168_677: ", square_168_677,  r_bytes, a_bytes);
  measure_squaring(t, "square_336_677: ", square_336_677, r_bytes, a_bytes);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_R2_tobytes(a_bytes, &a);
  }
  print_results("poly_R2_tobytes: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_R2_frombytes(&a, a_bytes);
  }
  print_results("poly_R2_frombytes: ", t, NTESTS);

  sample_iid(&a, uniformbytes);
  poly_Z3_to_Zq(&a);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_R2_inv(&r, &a);
  }
  print_results("poly_R2_inv: ", t, NTESTS);

  return 0;
}
