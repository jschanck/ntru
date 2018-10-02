#include <stdio.h>
#include "../params.h"
#include "../poly.h"
#include "../owcpa.h"
#include "../ntrukem.h"

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
  /* TODO: un-lazy reduce last coeff */
  poly_Rq_frombytes(c, packedct);
}

static void unpack_sk(poly *f, poly *finv3, const unsigned char *packedsk)
{
  int i;
  poly_S3_frombytes(f, packedsk);
  poly_S3_frombytes(finv3, packedsk+NTRU_PACK_TRINARY_BYTES);

  /* Lift coeffs of f from Z_p to Z_q */
  for(i=0; i<NTRU_N; i++)
    f->coeffs[i] = (f->coeffs[i] & 1) | ((-(f->coeffs[i]>>1)) & (NTRU_Q-1));
}

static void unpack_pk(poly *pk, const unsigned char *packedpk)
{
  poly_Rq_frombytes(pk, packedpk);
}

static void unpack_message(poly *m, const unsigned char *message)
{
  poly_S3_frombytes(m, message);
}

int main(void)
{
  unsigned char m_seed[32] = "ntru-kem n=701 owcpa test seed m";
  unsigned char r_seed[32] = "ntru-kem n=701 owcpa test seed r";
  unsigned char packed_pk[NTRU_OWCPA_PUBLICKEYBYTES];
  unsigned char packed_sk[NTRU_OWCPA_SECRETKEYBYTES];
  unsigned char packed_mA[NTRU_OWCPA_MSGBYTES];
  unsigned char packed_mB[NTRU_OWCPA_MSGBYTES];
  unsigned char packed_ct[NTRU_OWCPA_BYTES];
  poly pk, f, finv3, r, mA, ct, mB;

  owcpa_keypair(packed_pk, packed_sk);
  owcpa_samplemsg(packed_mA, m_seed);
  owcpa_enc(packed_ct, packed_mA, packed_pk, r_seed);
  owcpa_dec(packed_mB, packed_ct, packed_sk);
  poly_Rq_getnoise(&r, r_seed, 0);

  FILE *f_out = fopen("owcpa_vecs.txt", "w");

  unpack_pk(&pk, packed_pk);
  unpack_sk(&f, &finv3, packed_sk);
  unpack_ciphertext(&ct, packed_ct);
  unpack_message(&mA, packed_mA);
  unpack_message(&mB, packed_mB);

  poly_write(f_out, &f, "f");
  poly_write(f_out, &finv3, "fp");
  poly_write(f_out, &pk, "h");
  poly_write(f_out, &ct, "ct");
  poly_write(f_out, &r, "r");
  poly_write(f_out, &mA, "mA");
  poly_write(f_out, &mB, "mB");

  fclose(f_out);

  return 0;
}
