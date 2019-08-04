#ifndef RANDOMBYTES_H
#define RANDOMBYTES_H

void randombytes(unsigned char *x,unsigned long long xlen);
void fastrandombytes(unsigned char *x,unsigned long long xlen);

#define SHORTRANDOMBYTES randombytes
#define LONGRANDOMBYTES fastrandombytes

#endif
