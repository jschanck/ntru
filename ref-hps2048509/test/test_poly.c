#include <stdio.h>
#include <stdint.h>
#include "../poly.h"
#include "../sample.h"
#include "../randombytes.h"

int main(void)
{
  int i;
  int p1 = 0;
  int m1 = 0;

  unsigned char uniformbytes[NTRU_S3_FT_BYTES];
  randombytes(uniformbytes, sizeof(uniformbytes));

  poly a;
  sample_fixed_type(&a,uniformbytes);

  for(i=0; i<NTRU_N-1; i++)
  {
    p1 += a.coeffs[i] & 0x01;
    m1 += (a.coeffs[i] & 0x02) >> 1;
  }
  if(p1 != m1 || p1 + m1 != NTRU_WEIGHT)
    printf("Sample fixed type fails");

  return 0;
}
