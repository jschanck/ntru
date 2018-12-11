#include <stdio.h>
#include "../params.h"
#include "../poly.h"
#include "../randombytes.h"
#include "../verify.h"


#if 0
static void poly_print(poly *a)
{
  int i;
  printf("[");
  for(i=0; i<NTRU_N-1; i++)
    printf("%d, ", a->coeffs[i]);
  printf("%d]\n\n", a->coeffs[NTRU_N-1]);
}
#endif

int main(void)
{
  int i;
  int errorRq = 0;
  int errorS3 = 0;
  unsigned char p1[NTRU_OWCPA_BYTES];
  unsigned char p2[NTRU_PACK_TRINARY_BYTES];
  poly a, b, c;

  unsigned char seed[NTRU_SEEDBYTES];
  randombytes(seed, NTRU_SEEDBYTES);

  poly_S3_sample(&c,seed,0);
  poly_Z3_to_Zq(&c);
  poly_Rq_mul_x_minus_1(&a,&c); // We can only pack vectors with 0 coeff sum
  //poly_print(&a);
  poly_Rq_sum_zero_tobytes(p1, &a);
  poly_Rq_sum_zero_frombytes(&b, p1);
  //poly_print(&b);
  for(i=0; i<NTRU_N; i++)
    errorRq |= (a.coeffs[i] != b.coeffs[i]);

  if(errorRq)
    printf("Pack Rq fails\n");

  poly_S3_sample(&a,seed,0);
  //poly_print(&a);
  poly_S3_tobytes(p2, &a);
  poly_S3_frombytes(&b, p2);
  //poly_print(&b);
  for(i=0; i<NTRU_N; i++)
    errorS3 |= (a.coeffs[i] != b.coeffs[i]);

  if(errorS3)
    printf("Pack S3 fails\n");

  printf("TEST_PACK:\t%d\n", (errorS3 | errorRq) ? -1 : 0);
  return 0;
}
