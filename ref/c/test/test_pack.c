#include <stdio.h>
#include "../params.h"
#include "../poly.h"
#include "../randombytes.h"
#include "../verify.h"


static void poly_print(poly *a)
{
  int i;
  printf("[");
  for(i=0; i<NTRU_N-1; i++)
    printf("%d, ", a->coeffs[i]);
  printf("%d]\n\n", a->coeffs[NTRU_N-1]);
}

int main(void)
{
  int i;
  int error = 0;
  unsigned char p1[NTRU_OWCPA_BYTES];
  unsigned char p2[NTRU_PACK_TRINARY_BYTES];
  poly a, b;

  unsigned char seed[NTRU_SEEDBYTES];
  randombytes(seed, NTRU_SEEDBYTES);

  poly_Rq_getnoise(&a,seed,0);
  poly_Rq_tobytes(p1, &a);
  poly_Rq_frombytes(&b, p1);
  for(i=0; i<NTRU_N; i++)
    error |= (a.coeffs[i] != b.coeffs[i]);

  if(error)
    printf("Pack Rq fails\n");

  poly_S3_sample(&a,seed,0);
  poly_print(&a);
  poly_S3_tobytes(p2, &a);
  poly_S3_frombytes(&b, p2);
  poly_print(&b);
  for(i=0; i<NTRU_N; i++)
    error |= (a.coeffs[i] != b.coeffs[i]);

  if(error)
    printf("Pack S3 fails\n");

  return 0;
}
