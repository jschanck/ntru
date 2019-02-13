#include <stdio.h>
#include "../params.h"
#include "../poly.h"
#include "../owcpa.h"
#include "../kem.h"

static void poly_write(FILE *f, const poly *a, const char *var)
{
  int i;
  fprintf(f, "%s = [", var);
  for(i=0; i<NTRU_N-1; i++)
    fprintf(f, "%d, ", a->coeffs[i]);
  fprintf(f, "%d];\n", a->coeffs[NTRU_N-1]);
}

static void unpack_ciphertext(poly *c, const unsigned char *packedct)
{
  poly_Rq_sum_zero_frombytes(c, packedct);
}

static void unpack_sk(poly *f, poly *finv3, poly *hq, const unsigned char *packedsk)
{
  poly_S3_frombytes(f, packedsk);
  poly_Z3_to_Zq(f);
  poly_S3_frombytes(finv3, packedsk+NTRU_PACK_TRINARY_BYTES);
  poly_Rq_sum_zero_frombytes(hq, packedsk+2*NTRU_PACK_TRINARY_BYTES);
}

static void unpack_pk(poly *pk, const unsigned char *packedpk)
{
  poly_Rq_sum_zero_frombytes(pk, packedpk);
}

static void unpack_message(poly *r, poly *m, const unsigned char *message)
{
  poly_S3_frombytes(r, message);
  poly_S3_frombytes(m, message+NTRU_PACK_TRINARY_BYTES);
}

int main(void)
{
  unsigned char key_seed[32] = "ntruhrss701 owcpa test seed #000";
  unsigned char rm_seed[32] = "ntruhrss701 owcpa test seed #001";
  unsigned char packed_pk[NTRU_OWCPA_PUBLICKEYBYTES];
  unsigned char packed_sk[NTRU_OWCPA_SECRETKEYBYTES];
  unsigned char packed_rmA[NTRU_OWCPA_MSGBYTES];
  unsigned char packed_rmB[NTRU_OWCPA_MSGBYTES];
  unsigned char packed_ct[NTRU_OWCPA_BYTES];
  unsigned char packed_ct2[NTRU_OWCPA_BYTES];
  poly pk, f, finv3, hq, rA, mA, ct, rB, mB;

  owcpa_keypair(packed_pk, packed_sk, key_seed);
  owcpa_samplemsg(packed_rmA, rm_seed);
  owcpa_enc(packed_ct, packed_rmA, packed_pk);
  owcpa_dec(packed_ct2, packed_ct, packed_sk);

  FILE *out = fopen("owcpa_vecs.txt", "w");

  unpack_pk(&pk, packed_pk);
  unpack_sk(&f, &finv3, &hq, packed_sk);
  unpack_ciphertext(&ct, packed_ct);
  unpack_message(&rA, &mA, packed_rmA);
  unpack_message(&rB, &mB, packed_rmB);

  poly_write(out, &f, "f");
  poly_write(out, &finv3, "fp");
  poly_write(out, &pk, "h");
  poly_write(out, &ct, "ct");
  poly_write(out, &rA, "rA");
  poly_write(out, &mA, "mA");
  poly_write(out, &rB, "rB");
  poly_write(out, &mB, "mB");

  fclose(out);

  return 0;
}
