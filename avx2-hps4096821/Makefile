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

OBJS = square_1_821_patience.s \
	     square_3_821_patience.s \
	     square_6_821_patience.s \
	     square_12_821_shufbytes.s \
	     square_24_821_shufbytes.s \
	     square_51_821_shufbytes.s \
	     square_102_821_shufbytes.s \
	     square_204_821_shufbytes.s \
	     square_408_821_shufbytes.s

OBJS += poly_rq_mul.s \
        poly_r2_mul.s \
        poly_rq_to_s3.s \
        vec32_sample_iid.s \
        poly_mod_3_Phi_n.s \
        poly_mod_q_Phi_n.s

all: test/decap \
     test/encap \
     test/keypair \
     test/speed \
     test/speed_r2_inv \
     test/test_gp_compat \
     test/test_ntru \
     test/test_owcpa \
     test/test_pack

asm: ${OBJS} poly_s3_inv.c

poly_s3_inv.c: asmgen/poly_s3_inv.py
	NTRU_NAMESPACE=${NTRU_NAMESPACE} python3 $^ 820 | sed 's/4294967295/-1/g' > $@

poly_rq_mul.s: asmgen/rq_mul/poly_rq_mul.py asmgen/rq_mul/schoolbook_64x13.py asmgen/rq_mul/K2_K2_64x52.py
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

test/test_gp_compat: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_gp_compat.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_gp_compat.c

test/test_ntru: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_ntru.c

test/test_owcpa: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_owcpa.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_owcpa.c

test/test_pack: $(SRC_URAND) $(OBJS) $(HDR_URAND) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SRC_URAND) $(OBJS) test/test_pack.c

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

.PHONY: clean test

# Useful for the .s files;
.DELETE_ON_ERROR:

test: all
	./test/speed
	./test/speed_r2_inv
	./test/test_gp_compat | gp -q
	./test/test_ntru
	./test/test_pack

clean::
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -delete
	-$(RM) *.o
	-$(RM) *.s
	-$(RM) poly_s3_inv.c
	-$(RM) -r test/decap
	-$(RM) -r test/encap
	-$(RM) -r test/keypair
	-$(RM) -r test/speed
	-$(RM) -r test/speed_r2_inv
	-$(RM) -r test/test_gp_compat
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_owcpa
	-$(RM) -r test/test_pack
