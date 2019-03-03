#ifndef SAMPLE_H
#define SAMPLE_H

#include <stdlib.h>
#include "params.h"
#include "poly.h"

void sample_fg(poly *f, poly *g, const unsigned char uniformbytes[NTRU_SAMPLE_FG_BYTES]);
void sample_rm(poly *r, poly *m, const unsigned char uniformbytes[NTRU_SAMPLE_RM_BYTES]);

void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES]);

#ifdef NTRU_HPS /* hps needs sample_fixed_type */
void sample_fixed_type(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_FT_BYTES]);
#endif

#ifdef NTRU_HRSS /* hrss needs sample_iid_plus */
void sample_iid_plus(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES]);
#endif

#endif
