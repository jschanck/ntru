NTRU_NAMESPACE ?= ntru_

CC ?= /usr/bin/cc
CFLAGS = -O3 -fomit-frame-pointer -march=native -fPIC -fPIE -pie
CFLAGS += -Wall -Wextra -Wpedantic
CFLAGS += -DCRYPTO_NAMESPACE\(s\)=${NTRU_NAMESPACE}\#\#s

SRC = cmov.c \
      crypto_sort_int32.c \
      fips202.c \
      kem.c \
      owcpa.c \
      pack3.c \
      packq.c \
      poly.c \
      poly_lift.c \
      poly_r2_inv.c \
      poly_s3_inv.c \
      sample.c \
      sample_iid.c

HDR = cmov.h \
      crypto_sort_int32.h \
      kem.h \
      owcpa.h \
      params.h \
      poly.h \
      poly_r2_inv.h \
      sample.h

SRC_URAND = $(SRC) randombytes.c
HDR_URAND = $(HDR) randombytes.h

SRC_KAT = $(SRC) rng.c PQCgenKAT_kem.c
HDR_KAT = $(HDR) rng.h api.h

OBJS = square_1_677_patience.s \
       square_2_677_patience.s \
       square_3_677_patience.s \
       square_5_677_patience.s \
       square_10_677_shufbytes.s \
       square_21_677_shufbytes.s \
       square_42_677_shufbytes.s \
       square_84_677_shufbytes.s \
       square_168_677_shufbytes.s \
       square_336_677_shufbytes.s

OBJS += poly_rq_mul.s \
        poly_r2_mul.s \
        poly_rq_to_s3.s \
        vec32_sample_iid.s \
        poly_mod_3_Phi_n.s \
        poly_mod_q_Phi_n.s

all: test/test_polymul \
     test/test_ntru \
     test/test_owcpa \
     test/test_pack \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair \
     test/speed_r2_inv

asm: ${OBJS} poly_s3_inv.c

poly_s3_inv.c: asmgen/poly_s3_inv.py
	NTRU_NAMESPACE=${NTRU_NAMESPACE} python3 $^ 676 | sed 's/4294967295/-1/g' > $@

poly_rq_mul.s: asmgen/rq_mul/poly_rq_mul.py asmgen/rq_mul/K2_schoolbook_64x11.py asmgen/rq_mul/K2_K2_64x44.py
	NTRU_NAMESPACE=${NTRU_NAMESPACE} python3 $^ > $@

%.s: asmgen/%.py
	NTRU_NAMESPACE=${NTRU_NAMESPACE} python3 $^ > $@

square_%_shufbytes.s: $(wildcard bitpermutations/*)
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --shufbytes --namespace=$(NTRU_NAMESPACE) --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

square_%_patience.s: $(wildcard bitpermutations/*)
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --patience --callee 6 --namespace=$(NTRU_NAMESPACE) --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

test/test_polymul: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_polymul.c cpucycles.c

test/test_ntru: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_ntru.c cpucycles.c

test/test_owcpa: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_owcpa.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_owcpa.c

test/test_pack: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_pack.c cpucycles.c

test/ram: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/ram.c

test/speed: $(SRC_URAND) $(OBJS) $(HDR_URAND) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) cpucycles.c test/speed.c

test/speed_r2_inv: $(SRC_URAND) $(OBJS) $(HDR_URAND) cpucycles.h cpucycles.c test/speed_r2_inv.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) cpucycles.c test/speed_r2_inv.c

test/encap: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/encap.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/encap.c

test/decap: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/decap.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/decap.c

test/keypair: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/keypair.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/keypair.c

PQCgenKAT_kem: $(SRC_KAT) $(HDR_KAT) $(OBJS) 
	$(CC) $(CFLAGS) -o $@ $(SRC_KAT) $(OBJS) -lcrypto $(LDFLAGS)

.PHONY: clean test

# Useful for the .s files;
.DELETE_ON_ERROR:

test: all
	./test/test_polymul
	./test/test_ntru
	./test/test_pack
	./test/speed
	./test/ram
	./test/speed_r2_inv

clean:
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -delete
	-$(RM) *.o
	-$(RM) *.s
	-$(RM) poly_s3_inv.c
	-$(RM) -r test/test_polymul
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) -r test/speed
	-$(RM) -r test/ram
	-$(RM) -r test/encap
	-$(RM) -r test/decap
	-$(RM) -r test/keypair
	-$(RM) -r test/speed_r2_inv
	-$(RM) PQCgenKAT_kem
	-$(RM) PQCkemKAT_*.req
	-$(RM) PQCkemKAT_*.rsp
