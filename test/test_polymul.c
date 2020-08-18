#include <stdio.h>
#include <string.h>
#include "../poly.h"
#include "../sample.h"
#include "../randombytes.h"

/* Leaving this in here for debugging purposes. */
// static void poly_print(poly *a)
// {
//   int i;
//   printf("[");
//   for(i=0; i<NTRU_N-1; i++)
//     printf("%d, ", a->coeffs[i]);
//   printf("%d]\n\n", a->coeffs[NTRU_N-1]);
// }

static int poly_cmp1(poly *a)
{
  /* Since we're using the Almost Inverse algorithm, the result of multiplying
  a polynomial with its 'almost inverse' will be of the form [a+1, a, a, a, a]
  (instead of being [1, 0, 0, 0]). This is also accepted. */
  int i;
  for(i=1; i<NTRU_N; i++)
    if (a->coeffs[0] - a->coeffs[i] != 1)
      return -1;
  return 0;
}

static int test_poly_Rq_inv(poly *a)
{
  poly r1,r2;

  randombytes((unsigned char *)&r1, sizeof(poly));
  randombytes((unsigned char *)&r2, sizeof(poly));

  /* test inverse mod 2 */
  poly_Rq_inv(&r1, a);
  poly_Rq_mul(&r2, &r1, a);
  if(poly_cmp1(&r2))
    return -1;

  return 0;
}

static int test_poly_S3_inv(poly *a)
{
  poly r1,r2;

  for(int i=0; i<NTRU_N; i++)
  {
    r1.coeffs[i] = 0;
    r2.coeffs[i] = 0;
  }

  /* test inverse mod 2 */
  poly_S3_inv(&r1, a);
  poly_S3_mul(&r2, &r1, a);
  if(poly_cmp1(&r2))
    return -1;

  return 0;
}


static int test_lift()
{
  poly a, r1, r2;
  unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES];
  randombytes(uniformbytes, sizeof(uniformbytes));

  memset(&a,0,sizeof(poly));
  sample_iid(&a,uniformbytes);
  poly_lift(&r1, &a);
  poly_Rq_to_S3(&r2, &r1);

  return 0;
}

int main(void)
{
  unsigned char uniformbytes[2*NTRU_SAMPLE_IID_BYTES];
  randombytes(uniformbytes, sizeof(uniformbytes));

  poly a, b;
  sample_iid(&a,uniformbytes);
  poly_Z3_to_Zq(&a);
  sample_iid(&b,uniformbytes+NTRU_SAMPLE_IID_BYTES);

  printf("TEST_POLY_INV MOD2:\t%d\n", test_poly_Rq_inv(&a));
  printf("TEST_POLY_INV MOD3:\t%d\n", test_poly_S3_inv(&b));
  printf("TEST_LIFT:\t%d\n", test_lift());

  return 0;
}
