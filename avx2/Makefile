CC = /usr/bin/cc
CFLAGS = -O3 -Wall -Wextra -fomit-frame-pointer -march=native

SOURCES = poly.c fips202.c randombytes.c verify.c owcpa.c ntrukem.c poly_r2_inv.c
HEADERS = params.h poly.h randombytes.h verify.h owcpa.h ntrukem.h poly_r2_inv.h

OBJS = square_1_701_patience.s \
	   square_3_701_patience.s \
	   square_6_701_patience.s \
	   square_12_701_shufbytes.s \
	   square_15_701_shufbytes.s \
	   square_27_701_shufbytes.s \
	   square_42_701_shufbytes.s \
	   square_84_701_shufbytes.s \
	   square_168_701_shufbytes.s \
	   square_336_701_shufbytes.s
OBJS += poly_r2_mul.s poly_rq_mul.s poly_s3_mul.s poly_rq_mul_xm1.s
OBJS += poly_s3_inv.s poly_rq_to_s3.s poly_s3_to_rq.s cbds3.s

PATCHED = poly.c poly.h

all: test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/test_cshake \
     test/speed \
     test/ram \
     test/speed_r2_inv \

poly_rq_mul.s: asmgen/rq_mul/poly_rq_mul.py asmgen/rq_mul/K2_schoolbook_64x11.py asmgen/rq_mul/K2_K2_64x44.py
	python3 $^ > $@

%.s: asmgen/%.py
	python3 $^ > $@

$(PATCHED): %: %.patch %.unpatched
	cp --dereference $@.unpatched $@
	patch $@ $@.patch

square_%_701.s: $(wildcard bitpermutations/*)
	@git submodule update --init bitpermutations
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

square_%_701_shufbytes.s: $(wildcard bitpermutations/*)
	@git submodule update --init bitpermutations
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --shufbytes --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

square_%_701_patience.s: $(wildcard bitpermutations/*)
	@git submodule update --init bitpermutations
	PYTHONPATH=bitpermutations \
	 python3 bitpermutations/applications/squaring_mod_GF2N.py \
	 --patience --callee 6 --raw-name $(word 2, $(subst _, ,$@)) \
	 > $@

test/test_polymul: $(SOURCES) $(OBJS) $(HEADERS) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_polymul.c cpucycles.c

test/test_ntru: $(SOURCES) $(OBJS) $(HEADERS) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_ntru.c cpucycles.c

test/test_pack: $(SOURCES) $(OBJS) $(HEADERS) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/test_pack.c cpucycles.c

test/ram: $(SOURCES) $(OBJS) $(HEADERS) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/ram.c

test/speed: $(SOURCES) $(OBJS) $(HEADERS) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) cpucycles.c test/speed.c

test/speed_r2_inv: $(SOURCES) $(OBJS) $(HEADERS) cpucycles.h cpucycles.c test/speed_r2_inv.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) cpucycles.c test/speed_r2_inv.c

test/test_cshake: fips202.h fips202.c test/test_cshake.c
	$(CC) $(CFLAGS) -o $@ fips202.c test/test_cshake.c

.PHONY: clean test

# In particular useful for the .s files;
.DELETE_ON_ERROR:

test:
	./test/test_polymul
	./test/test_ntru
	./test/test_pack
	./test/test_cshake
	./test/speed
	./test/speed_r2_inv

clean:
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -delete
	-$(RM) *.o
	-$(RM) *.s
	-$(RM) $(PATCHED)
	-$(RM) -r test/test_polymul
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) -r test/test_cshake
	-$(RM) -r test/speed
	-$(RM) -r test/ram
	-$(RM) -r test/speed_r2_inv
