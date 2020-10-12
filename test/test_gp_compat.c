#include "../poly.h"
#include "../sample.h"
#include "../randombytes.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#define S1(x) #x
#define S(x) S1(x)

#define Q S(NTRU_Q)
#define N S(NTRU_N)

#define CHECK(label, test) printf("OK=("test");\nif(!OK,ALLOK=0;printf(\"error in "#label"\\n\"));\n\n")

static void poly_sprint(char *out, poly *a)
{
  int i, x;
  x = sprintf(out, "[");
  out += x;
  for(i=0; i<NTRU_N-1; i++)
  {
    x = sprintf(out, "%" PRIu16 ",", a->coeffs[i]);
    out += x;
  }
  sprintf(out, "%" PRIu16 "]", a->coeffs[NTRU_N-1]);
}

int main(void)
{
  int i;
  unsigned char uniformbytes[2*NTRU_SAMPLE_IID_BYTES];

  /* up to 5 decimals per coefficient plus commas, brackets, and null terminator */
  char s1[5*NTRU_N + NTRU_N + 3];
  char s2[5*NTRU_N + NTRU_N + 3];
  char s3[5*NTRU_N + NTRU_N + 3];

  poly in, in2, out;

  printf("ALLOK=1;\n");
  printf("plift(x) = lift(lift(x));\n");
  /*  Pari/GP center lifts to (-q/2, q/2] instead of [-q/2, q/2) */
  printf("clift(x) = if(type(x) == \"t_POLMOD\", -centerlift(-lift(x)), -centerlift(-x));\n");
  printf("q = "Q";\n");
  printf("n = "N";\n");
  printf("Phi = polcyclo(n);\n");

  /* Test poly_Z3_to_Zq */
  randombytes(uniformbytes, sizeof(uniformbytes));
  sample_iid(&in,uniformbytes);
  for(i=0; i<NTRU_N; i++) out.coeffs[i] = in.coeffs[i];
  poly_Z3_to_Zq(&out);
  poly_sprint(s1, &in); printf("in = Mod(1,3) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_Z3_to_Zq, "out == plift(Mod(clift(in), q))");

  /* Test poly_trinary_Zq_to_Z3 */
  randombytes(uniformbytes, sizeof(uniformbytes));
  sample_iid(&in,uniformbytes);
  poly_Z3_to_Zq(&in);
  for(i=0; i<NTRU_N; i++) out.coeffs[i] = in.coeffs[i];
  poly_trinary_Zq_to_Z3(&out);
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_trinary_Zq_to_Z3, "out == plift(Mod(1,3) * clift(in))");

  /* Test poly_Rq_mul */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  randombytes((unsigned char *)&in2.coeffs, sizeof(in2.coeffs));
  poly_Rq_mul(&out, &in, &in2);
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &in2); printf("in2 = Mod(1,q) * Polrev(%s);\n", s2);
  poly_sprint(s3, &out); printf("out = Mod(1,q) * Polrev(%s);\n", s3);
  CHECK(poly_Rq_mul, "plift(out) == plift(Mod(in*in2, x^n-1))");

  /* Test poly_Sq_mul */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  randombytes((unsigned char *)&in2.coeffs, sizeof(in2.coeffs));
  in.coeffs[NTRU_N-1] = 0;
  in2.coeffs[NTRU_N-1] = 0;
  poly_Sq_mul(&out, &in, &in2);
  out.coeffs[NTRU_N-1] = 0;
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &in2); printf("in2 = Mod(1,q) * Polrev(%s);\n", s2);
  poly_sprint(s3, &out); printf("out = Mod(1,q) * Polrev(%s);\n", s3);
  CHECK(poly_Sq_mul, "plift(out) == plift(Mod(in*in2, Phi))");

  /* Test poly_S3_mul */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  randombytes((unsigned char *)&in2.coeffs, sizeof(in2.coeffs));
  for(i=0; i<NTRU_N; i++) in.coeffs[i] %= 3;
  for(i=0; i<NTRU_N; i++) in2.coeffs[i] %= 3;
  in.coeffs[NTRU_N-1] = 0;
  in2.coeffs[NTRU_N-1] = 0;
  poly_S3_mul(&out, &in, &in2);
  out.coeffs[NTRU_N-1] = 0;
  poly_sprint(s1, &in); printf("in = Mod(1,3) * Polrev(%s);\n", s1);
  poly_sprint(s2, &in2); printf("in2 = Mod(1,3) * Polrev(%s);\n", s2);
  poly_sprint(s3, &out); printf("out = Polrev(%s);\n", s3);
  CHECK(poly_S3_mul, "out == plift(Mod(in*in2, Phi))");

  /* Test poly_R2_inv */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  for(i=0; i<NTRU_N; i++) in.coeffs[i] %= 2;
  poly_R2_inv(&out, &in);
  poly_sprint(s1, &in); printf("in = Mod(1,2) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_R2_inv, "1 == plift(Mod(in*out, Phi))");

  /* Test poly_Rq_inv */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  poly_Rq_inv(&out, &in);
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Mod(1,q) * Polrev(%s);\n", s2);
  CHECK(poly_Rq_inv, "1 == plift(Mod(in*out, Phi))");

  /* Test poly_S3_inv */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  for(i=0; i<NTRU_N-1; i++) in.coeffs[i] %= 3;
  in.coeffs[NTRU_N-1] = 0;
  poly_S3_inv(&out, &in);
  out.coeffs[NTRU_N-1] = 0;
  poly_sprint(s1, &in); printf("in = Mod(1,3) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Mod(1,3) * Polrev(%s);\n", s2);
  CHECK(poly_S3_inv, "1 == plift(Mod(in*out, Phi))");

  /* Test poly_mod_3_Phi_n */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  for(i=0; i<NTRU_N; i++) in.coeffs[i] %= 3;
  for(i=0; i<NTRU_N; i++) out.coeffs[i] = in.coeffs[i];
  poly_mod_3_Phi_n(&out);
  poly_sprint(s1, &in); printf("in = Mod(1,3) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_mod_3_Phi_n, "out == plift(Mod(in, Phi))");

  /* Test poly_mod_q_Phi_n */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  for(i=0; i<NTRU_N; i++) out.coeffs[i] = in.coeffs[i];
  poly_mod_q_Phi_n(&out); // Does not actually reduce mod q.
  for(i=0; i<NTRU_N; i++) out.coeffs[i] %= NTRU_Q;
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_mod_q_Phi_n, "out == plift(Mod(in, Phi))");

  /* Test poly_Rq_to_S3 */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  in.coeffs[0] = NTRU_Q/2; /* Ensure we test reduction of q/2 */
  in.coeffs[NTRU_N-1] = 1; /* Ensure reduction mod Phi is non-trivial */
  poly_Rq_to_S3(&out, &in);
  poly_sprint(s1, &in); printf("in = Mod(1,q) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Polrev(%s);\n", s2);
  CHECK(poly_Rq_to_S3, "out == plift(Mod(Mod(1,3) * clift(in),Phi))");

#ifdef NTRU_HRSS
  /* Test poly_lift */
  randombytes((unsigned char *)&in.coeffs, sizeof(in.coeffs));
  for(i=0; i<NTRU_N-1; i++) in.coeffs[i] %= 3;
  in.coeffs[NTRU_N-1] = 0;
  poly_lift(&out, &in);
  poly_sprint(s1, &in); printf("in = Mod(1,3) * Polrev(%s);\n", s1);
  poly_sprint(s2, &out); printf("out = Mod(1,q) * Polrev(%s);\n", s2);
  CHECK(poly_lift, "plift(out) == plift(Mod(1,q) * (x-1) * clift((Mod(in / (x-1), Phi))))");
#endif

  printf("if(ALLOK, printf(\"success\\n\\n\"))");
  printf("\n\n\\\\ You probably wanted to run: './test/test_gp_compat | gp -q'\n");

  return 0;
}
