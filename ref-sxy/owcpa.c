#include "owcpa.h"
#include "poly.h"
#include "randombytes.h"

#define MODQ(X) ((X) & (NTRU_Q-1))

#define DOMM 0
#define DOMF 1
#define DOMG 2
#define DOMR 3

static int owcpa_check_r(const poly *r)
{
  /* Check that r has coefficients in {0,1,q-1} and r_{n-1} = 0. */
  int i;
  uint64_t t = 0;
  uint16_t c;
  for(i=0; i<NTRU_N; i++)
  {
    c = MODQ(r->coeffs[i]+1);
    t |= c & (NTRU_Q-4);  /* 0 if c is in {0,1,2,3} */
    t |= (c + 1) & 0x4;   /* 0 if c is in {0,1,2} */
  }
  t |= r->coeffs[NTRU_N-1]; /* Coefficient n-1 must be zero */
  t = (-t) >> 63;
  return t;
}

void owcpa_samplemsg(unsigned char msg[NTRU_OWCPA_MSGBYTES],
                     const unsigned char seed[NTRU_SEEDBYTES])
{
  poly r, m;

  poly_S3_sample(&r,seed,DOMR);
  poly_S3_sample(&m,seed,DOMM);

  poly_S3_tobytes(msg, &r);
  poly_S3_tobytes(msg+NTRU_PACK_TRINARY_BYTES, &m);
}

void owcpa_keypair(unsigned char *pk,
                   unsigned char *sk,
                   const unsigned char seed[NTRU_SEEDBYTES])
{
  int i;
  uint16_t t;

  poly x1, x2, x3, x4, x5;

  poly *f=&x1, *invf_mod3=&x2;
  poly *g=&x3, *G=&x2;
  poly *Gf=&x3, *invGf=&x4, *tmp=&x5;
  poly *invh=&x3, *h=&x3;

  poly_S3_sample_plus(f,seed,DOMF);

  poly_S3_inv(invf_mod3, f);

  poly_S3_tobytes(sk, f);
  poly_S3_tobytes(sk+NTRU_PACK_TRINARY_BYTES, invf_mod3);

  /* Lift coeffs of f and g from Z_p to Z_q */
  poly_Z3_to_Zq(f);

  poly_S3_sample_plus(g,seed,DOMG);
  poly_Z3_to_Zq(g);

  /* G = 3*(x-1)*g */
  poly_Rq_mul_x_minus_1(G, g);
  for(i=0; i<NTRU_N; i++)
    G->coeffs[i] = MODQ(3 * G->coeffs[i]);

  poly_Rq_mul(Gf, G, f);

  poly_Rq_inv(invGf, Gf);

  poly_Rq_mul(tmp, invGf, f);
  poly_Rq_mul(invh, tmp, f);

  /* We really only need invh mod (q, Phi_n), but we  */
  /* don't have a dedicated encoding routine for      */
  /* arbitrary degree 699 polynomials. We do have an  */
  /* encoding routine for degree 700 polynomials with */
  /* coefficients that sum to 0 (which uses the same  */
  /* amount of space). So we'll just add a multiple   */
  /* of Phi_n and use the existing routine.           */
  t=0;
  for(i=0; i<NTRU_N; i++)
    t = t + invh->coeffs[i];
  t = MODQ(t*NTRU_N_INVERSE_MOD_Q);
  for(i=0; i<NTRU_N; i++)
    invh->coeffs[i] = MODQ(invh->coeffs[i] - t);

  poly_Rq_sum_zero_tobytes(sk+2*NTRU_PACK_TRINARY_BYTES, invh);

  poly_Rq_mul(tmp, invGf, G);
  poly_Rq_mul(h, tmp, G);

  poly_Rq_sum_zero_tobytes(pk, h);
}


void owcpa_enc(unsigned char *c,
               const unsigned char *rm,
               const unsigned char *pk)
{
  int i;
  poly x1, x2, x3;
  poly *h = &x1, *liftm = &x1;
  poly *r = &x2, *m = &x2;
  poly *ct = &x3;

  poly_Rq_sum_zero_frombytes(h, pk);

  poly_S3_frombytes(r, rm);
  poly_Z3_to_Zq(r);

  poly_Rq_mul(ct, r, h);

  poly_S3_frombytes(m, rm+NTRU_PACK_TRINARY_BYTES);
  poly_S3_to_Rq(liftm, m);
  for(i=0; i<NTRU_N; i++)
    ct->coeffs[i] = MODQ(ct->coeffs[i] + liftm->coeffs[i]);

  poly_Rq_sum_zero_tobytes(c, ct);
}

int owcpa_dec_and_reenc(unsigned char *c2,
                        unsigned char *rm,
                        const unsigned char *ciphertext,
                        const unsigned char *secretkey)
{
  int i;
  int fail;
  poly x1, x2, x3, x4;

  poly *c = &x1, *f = &x2, *cf = &x3;
  poly *mf = &x2, *finv3 = &x3, *m = &x4;
  poly *liftm = &x2, *invh = &x3, *r = &x4;
  poly *b = &x1;

  uint16_t t;

  poly_Rq_sum_zero_frombytes(c, ciphertext);
  poly_S3_frombytes(f, secretkey);
  poly_Z3_to_Zq(f);

  poly_Rq_mul(cf, c, f);
  poly_Rq_to_S3(mf, cf);

  poly_S3_frombytes(finv3, secretkey+NTRU_PACK_TRINARY_BYTES);
  poly_S3_mul(m, mf, finv3);
  poly_S3_tobytes(rm+NTRU_PACK_TRINARY_BYTES, m);
  poly_S3_to_Rq(liftm, m);

  /* b = ct - Lift(m) mod (q, Phi_n) */
  for(i=0; i<NTRU_N; i++)
    b->coeffs[i] = MODQ(c->coeffs[i] - liftm->coeffs[i]);
  for(i=0; i<NTRU_N; i++)
    b->coeffs[i] = MODQ(b->coeffs[i] - b->coeffs[NTRU_N-1]);

  /* r = b / h mod (q, Phi_n) */
  poly_Rq_sum_zero_frombytes(invh, secretkey+2*NTRU_PACK_TRINARY_BYTES);
  poly_Rq_mul(r, b, invh);
  for(i=0; i<NTRU_N; i++)
    r->coeffs[i] = MODQ(r->coeffs[i] - r->coeffs[NTRU_N-1]);

  /* NOTE: We can re-encaps with b, instead of computing rh, as long as  */
  /* we check that r has coefficients in {-1,0,1} and has r_{n-1} = 0.   */
  /* It is important not to reduce r mod 3 (or perform any other         */
  /* non-invertible operations) before this check.                       */
  /* All m in the domain of poly_S3_to_Rq are OK, so no need to check m. */
  fail = owcpa_check_r(r);

  poly_trinary_Zq_to_Z3(r);
  poly_S3_tobytes(rm, r);

  /* t = -(b(1) / n) mod q */
  t = 0;
  for(i=0; i<NTRU_N; i++)
    t = t + b->coeffs[i];
  t = MODQ(t * NTRU_N_INVERSE_MOD_Q);
  for(i=0; i<NTRU_N; i++)
    b->coeffs[i] = MODQ(b->coeffs[i] - t + liftm->coeffs[i]);

  poly_Rq_sum_zero_tobytes(c2, b);

  return fail;
}
