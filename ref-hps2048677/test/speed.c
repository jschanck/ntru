#include "../kem.h"
#include "../params.h"
#include "../cpucycles.h"
#include "../randombytes.h"
#include "../poly.h"
#include "../sample.h"
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

int main()
{
  unsigned char key_a[32], key_b[32];
  poly r, a, b;
  unsigned char* pks = (unsigned char*) malloc(NTESTS*NTRU_PUBLICKEYBYTES);
  unsigned char* sks = (unsigned char*) malloc(NTESTS*NTRU_SECRETKEYBYTES);
  unsigned char* cts = (unsigned char*) malloc(NTESTS*NTRU_CIPHERTEXTBYTES);
  unsigned char uniformbytes[2*NTRU_SAMPLE_IID_BYTES+NTRU_SAMPLE_FT_BYTES];
  unsigned char seed[NTRU_SEEDBYTES];
  unsigned long long t[NTESTS];
  uint16_t a1 = 0;
  int i;

  printf("-- api --\n\n");

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    crypto_kem_keypair(pks+i*NTRU_PUBLICKEYBYTES,
                       sks+i*NTRU_SECRETKEYBYTES);
  }
  print_results("ntru_keypair: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    crypto_kem_enc(cts+i*NTRU_CIPHERTEXTBYTES, key_b, pks+i*NTRU_PUBLICKEYBYTES);
  }
  print_results("ntru_encaps: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    crypto_kem_dec(key_a, cts+i*NTRU_CIPHERTEXTBYTES, sks+i*NTRU_SECRETKEYBYTES);
  }
  print_results("ntru_decaps: ", t, NTESTS);

  printf("-- internals --\n\n");

  randombytes(uniformbytes, sizeof(uniformbytes));
  sample_iid(&a, uniformbytes);
  sample_iid(&b, uniformbytes+NTRU_SAMPLE_IID_BYTES);
  poly_Z3_to_Zq(&a);
  poly_Z3_to_Zq(&b);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_mul(&r, &a, &b);
  }
  print_results("poly_Rq_mul: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_S3_mul(&r, &a, &b);
  }
  print_results("poly_S3_mul: ", t, NTESTS);

  // a as generated in test_polymul
  for(i=0; i<NTRU_N; i++)
    a1 += a.coeffs[i];
  a.coeffs[0] = (a.coeffs[0] + (1 ^ (a1&1))) & 3;

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_mul_x_minus_1(&r, &a);
  }
  print_results("poly_Rq_mul_x_minus_1: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_inv(&r, &a);
  }
  print_results("poly_Rq_inv: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_S3_inv(&r, &a);
  }
  print_results("poly_S3_inv: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    sample_xof(uniformbytes, NTRU_SAMPLE_IID_BYTES, seed);
  }
  print_results("sample_xof (for iid poly_S3): ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    sample_xof(uniformbytes, NTRU_SAMPLE_FT_BYTES, seed);
  }
  print_results("sample_xof (for fixed type poly_S3): ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    sample_iid(&a, uniformbytes);
  }
  print_results("sample_iid: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    sample_fixed_type(&a, uniformbytes);
  }
  print_results("sample_fixed_type: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_lift(&a, &b);
  }
  print_results("poly_lift: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_to_S3(&a, &b);
  }
  print_results("poly_Rq_to_S3: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_sum_zero_tobytes(cts, &a);
  }
  print_results("poly_Rq_sum_zero_tobytes: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_Rq_sum_zero_frombytes(&a, cts);
  }
  print_results("poly_Rq_sum_zero_frombytes: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_S3_tobytes(cts, &b);
  }
  print_results("poly_S3_tobytes: ", t, NTESTS);

  for(i=0; i<NTESTS; i++)
  {
    t[i] = cpucycles();
    poly_S3_frombytes(&b, cts);
  }
  print_results("poly_S3_frombytes: ", t, NTESTS);

  free(pks);
  free(sks);
  free(cts);

  return 0;
}
