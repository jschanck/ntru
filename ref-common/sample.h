#ifndef SAMPLE_H
#define SAMPLE_H

#include "params.h"
#include "poly.h"

#ifdef NTRU_HPS
#include "crypto_sort_int32.h"
#endif

#define sample_fg CRYPTO_NAMESPACE(sample_fg)
#define sample_rm CRYPTO_NAMESPACE(sample_rm)
void sample_fg(poly *f, poly *g, const unsigned char uniformbytes[NTRU_SAMPLE_FG_BYTES]);
void sample_rm(poly *r, poly *m, const unsigned char uniformbytes[NTRU_SAMPLE_RM_BYTES]);

#define sample_iid CRYPTO_NAMESPACE(sample_iid)
void sample_iid(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES]);

#ifdef NTRU_HPS /* hps needs sample_fixed_type */
#define sample_fixed_type CRYPTO_NAMESPACE(sample_fixed_type)
void sample_fixed_type(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_FT_BYTES]);
#endif

#ifdef NTRU_HRSS /* hrss needs sample_iid_plus */
#define sample_iid_plus CRYPTO_NAMESPACE(sample_iid_plus)
void sample_iid_plus(poly *r, const unsigned char uniformbytes[NTRU_SAMPLE_IID_BYTES]);
#endif

#endif
