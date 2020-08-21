CC ?= /usr/bin/cc
CFLAGS = -O3 -fomit-frame-pointer -march=native -fPIC -fPIE -pie
CFLAGS += -Wall -Wextra -Wpedantic

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

all: test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair

test/test_polymul: $(SRC_URAND) $(HDR_URAND) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_polymul.c

test/test_ntru: $(SRC_URAND) $(HDR_URAND) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_ntru.c

test/test_pack: $(SRC_URAND) $(HDR_URAND) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) test/test_pack.c

test/speed: $(SRC_URAND) $(HDR_URAND) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) cpucycles.c test/speed.c

test/ram: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/ram.c

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
	./test/test_polymul
	./test/test_ntru
	./test/test_pack
	./test/speed
	./test/ram

clean:
	-$(RM) *.o
	-$(RM) -r test/test_polymul
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) -r test/speed
	-$(RM) -r test/ram
	-$(RM) -r test/encap
	-$(RM) -r test/decap
	-$(RM) -r test/keypair
	-$(RM) PQCgenKAT_kem
	-$(RM) PQCkemKAT_*.req
	-$(RM) PQCkemKAT_*.rsp
