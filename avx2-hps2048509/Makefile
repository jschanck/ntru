CC = /usr/bin/cc
CFLAGS = -Wall -Wextra -Wpedantic -O3 -fomit-frame-pointer -march=native -fPIC -fPIE -pie

SOURCES = crypto_sort.c djbsort/sort.c poly.c poly_s3_inv.c poly_r2_inv.c pack3.c packq.c fips202.c randombytes.c sample.c verify.c owcpa.c kem.c
HEADERS = crypto_sort.h djbsort/int32_sort.h poly_s3_inv.h poly_r2_inv.h params.h poly.h randombytes.h sample.h verify.h owcpa.h kem.h


OBJS = square_1_509_patience.s \
	   square_3_509_patience.s \
	   square_6_509_patience.s \
	   square_15_509_shufbytes.s \
	   square_30_509_shufbytes.s \
	   square_63_509_shufbytes.s \
	   square_126_509_shufbytes.s \
	   square_252_509_shufbytes.s
OBJS += poly_mod3.s poly_rq_mul.s poly_r2_mul.s poly_s3_mul.s poly_rq_mul_x_minus_1.s poly_rq_to_s3.s sample_iid.s

all: test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair \
     test/gen_owcpa_vecs

poly_rq_mul.s: asmgen/rq_mul/poly_rq_mul.py asmgen/rq_mul/K2_schoolbook_64x8.py asmgen/rq_mul/K2_K2_64x32.py
	python3 $^ > $@

%.s: asmgen/%.py
	python3 $^ > $@

square_%_509_shufbytes.s: $(wildcard bitpermutations/*)
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --shufbytes --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

square_%_509_patience.s: $(wildcard bitpermutations/*)
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --patience --callee 6 --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

test/test_polymul: $(SOURCES) $(OBJS) $(HEADERS) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_polymul.c

test/test_ntru: $(SOURCES) $(OBJS) $(HEADERS) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_ntru.c

test/test_pack: $(SOURCES) $(OBJS) $(HEADERS) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_pack.c

test/speed: $(SOURCES) $(OBJS) $(HEADERS) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) cpucycles.c test/speed.c

test/ram: $(SOURCES) $(OBJS) $(HEADERS) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/ram.c

test/gen_owcpa_vecs: $(SOURCES) $(OBJS) $(HEADERS) test/gen_owcpa_vecs.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/gen_owcpa_vecs.c

test/encap: $(SOURCES) $(OBJS) $(HEADERS) test/encap.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/encap.c

test/decap: $(SOURCES) $(OBJS) $(HEADERS) test/decap.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/decap.c

test/keypair: $(SOURCES) $(OBJS) $(HEADERS) test/keypair.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/keypair.c

.PHONY: clean test

# In particular useful for the .s files;
.DELETE_ON_ERROR:

test:
	./test/test_polymul
	./test/test_ntru
	./test/test_pack
	./test/speed
	./test/ram

clean:
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -delete
	-$(RM) *.o
	-$(RM) *.s
	-$(RM) -r test/test_polymul
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) -r test/speed
	-$(RM) -r test/ram
	-$(RM) -r test/encap
	-$(RM) -r test/decap
	-$(RM) -r test/keypair
	-$(RM) -r test/gen_owcpa_vecs
