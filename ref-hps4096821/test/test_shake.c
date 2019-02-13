#include <stdio.h>
#include "../fips202.h"

const unsigned char *input = (unsigned char*)"The quick brown fox jumps over the lazy dog";
const unsigned char result[] = {0xf4, 0x20, 0x2e, 0x3c, 0x58, 0x52, 0xf9, 0x18,
                                0x2a, 0x04, 0x30, 0xfd, 0x81, 0x44, 0xf0, 0xa7,
                                0x4b, 0x95, 0xe7, 0x41, 0x7e, 0xca, 0xe1, 0x7d,
                                0xb0, 0xf8, 0xcf, 0xee, 0xd0, 0xe3, 0xe6, 0x6e};

int main(void)
{
  unsigned char hash[32];
  int i;

  shake128(hash, 32, input, 43);

  for(i=0;i<32;i++)
    printf("%02x ", result[i]);
  printf("\n");

  for(i=0;i<32;i++)
    printf("%02x ", hash[i]);
  printf("\n");

  for(i=0;i<32;i++) {
    if (hash[i] != result[i]) {
      printf("Failed!\n");
      return 1;
    }
  }
  printf("Success!\n");

  return 0;
}
