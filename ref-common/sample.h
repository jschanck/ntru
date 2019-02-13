#ifndef SAMPLE_H
#define SAMPLE_H

#include <stdlib.h>
#include "params.h"
#include "poly.h"

void sample_xof(unsigned char *output, const size_t sizeof_output, const unsigned char seed[NTRU_SEEDBYTES], const unsigned char domain[NTRU_DOMAINBYTES]);
void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_S3_IID_BYTES]);

/* XXX Dedicated define for this */
#ifdef NTRU_S3_FT_BYTES /* hps needs sample_fixed_type */
void sample_fixed_type(poly *r, const unsigned char uniformbytes[NTRU_S3_FT_BYTES]);
#else /* hrss needs sample_iid_plus */
void sample_iid_plus(poly *r, const unsigned char uniformbytes[NTRU_S3_IID_BYTES]);
#endif

#endif
