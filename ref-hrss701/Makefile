NTRU_NAMESPACE ?= ntru_

CC ?= /usr/bin/cc
CFLAGS = -O3 -fomit-frame-pointer -march=native -fPIC -fPIE -pie
CFLAGS += -Wall -Wextra -Wpedantic
CFLAGS += -DCRYPTO_NAMESPACE\(s\)=${NTRU_NAMESPACE}\#\#s

SRC = cmov.c \
      fips202.c \
      kem.c \
      owcpa.c \
      pack3.c \
      packq.c \
      poly.c \
      poly_lift.c \
      poly_mod.c \
      poly_r2_inv.c \
      poly_rq_mul.c \
      poly_s3_inv.c \
      sample.c \
      sample_iid.c

HDR = cmov.h \
      crypto_hash_sha3256.h \
      kem.h \
      owcpa.h \
      params.h \
      poly.h \
      sample.h

SRC_URAND = $(SRC) randombytes.c
HDR_URAND = $(HDR) randombytes.h

SRC_KAT = $(SRC) rng.c PQCgenKAT_kem.c
HDR_KAT = $(HDR) rng.h api.h

all: test/decap \
     test/encap \
     test/keypair \
     test/speed \
     test/test_gp_compat \
     test/test_ntru \
     test/test_owcpa \
     test/test_pack

test/test_gp_compat: $(SRC_URAND) $(HDR_URAND) test/test_gp_compat.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_gp_compat.c

test/test_ntru: $(SRC_URAND) $(HDR_URAND) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_ntru.c

test/test_owcpa: $(SRC_URAND) $(HDR_URAND) test/test_owcpa.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_owcpa.c

test/test_pack: $(SRC_URAND) $(HDR_URAND) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_pack.c

test/speed: $(SRC_URAND) $(HDR_URAND) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) cpucycles.c test/speed.c

test/gen_owcpa_vecs: test/gen_owcpa_vecs.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/gen_owcpa_vecs.c

test/encap: $(SRC_URAND) $(HDR_URAND) test/encap.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/encap.c

test/decap: $(SRC_URAND) $(HDR_URAND) test/decap.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/decap.c

test/keypair: $(SRC_URAND) $(HDR_URAND) test/keypair.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/keypair.c

PQCgenKAT_kem: $(SRC_KAT) $(HDR_KAT)
	$(CC) $(CFLAGS) -o $@ $(SRC_KAT) -lcrypto $(LDFLAGS)

.PHONY: clean test

test: all
	./test/speed
	./test/test_gp_compat | gp -q
	./test/test_ntru
	./test/test_pack

clean:
	-$(RM) *.o
	-$(RM) -r test/decap
	-$(RM) -r test/encap
	-$(RM) -r test/keypair
	-$(RM) -r test/speed
	-$(RM) -r test/test_gp_compat
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) PQCgenKAT_kem
	-$(RM) PQCkemKAT_*.req
	-$(RM) PQCkemKAT_*.rsp
