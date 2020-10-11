#include <stdio.h>
#include "../params.h"
#include "../poly.h"
#include "../sample.h"
#include "../randombytes.h"

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

  unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES];
  randombytes(uniformbytes, sizeof(uniformbytes));

  sample_iid(&c,uniformbytes);
  poly_Z3_to_Zq(&c);
  for(i=NTRU_N-1; i>0; i--)
    a.coeffs[i] = (c.coeffs[i-1] - c.coeffs[i]);
  a.coeffs[0] = -(c.coeffs[0]);
  //poly_print(&a);
  poly_Rq_sum_zero_tobytes(p1, &a);
  poly_Rq_sum_zero_frombytes(&b, p1);
  //poly_print(&b);
  for(i=0; i<NTRU_N; i++)
    errorRq |= (MODQ(a.coeffs[i]) != MODQ(b.coeffs[i]));

  if(errorRq)
    printf("Pack Rq fails\n");

  sample_iid(&a,uniformbytes);
  //poly_print(&a);
  poly_S3_tobytes(p2, &a);
  poly_S3_frombytes(&b, p2);
  //poly_print(&b);
  for(i=0; i<NTRU_N; i++)
    errorS3 |= (a.coeffs[i] != b.coeffs[i]);

  if(errorS3)
    printf("Pack S3 fails\n");

  if (!(errorS3 | errorRq))
    printf("success\n\n");
  return 0;
}
