#include <stdio.h>
#include "../fips202.h"

const char *custom = "Email Signature";

const unsigned char data[4] = {0,1,2,3};


int main(void)
{
  unsigned char hash[32];
  int i;

  
  cshake128_256simple(hash, custom, data, 4);

  for(i=0;i<32;i++)
    printf("%02x ", hash[i]);
  printf("\n");

  return 0;
}
