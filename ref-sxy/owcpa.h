#ifndef OWCPA_H
#define OWCPA_H

#include "params.h"

void owcpa_samplemsg(unsigned char msg[NTRU_OWCPA_MSGBYTES],
                     unsigned char seed[NTRU_SEEDBYTES]);

void owcpa_keypair(unsigned char *pk, 
                   unsigned char *sk);

void owcpa_enc(unsigned char *c,
               const unsigned char *rm,
               const unsigned char *pk);

int owcpa_dec_and_reenc(unsigned char *c2,
                        unsigned char *rm,
                        const unsigned char *c,
                        const unsigned char *sk);
#endif
