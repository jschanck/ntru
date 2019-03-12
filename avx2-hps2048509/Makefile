CC = /usr/bin/cc
CFLAGS = -Wall -Wextra -Wpedantic -O3 -fomit-frame-pointer -march=native -no-pie

SOURCES = crypto_sort.c poly.c pack3.c packq.c fips202.c randombytes.c sample.c verify.c owcpa.c kem.c
HEADERS = crypto_sort.h params.h poly.h randombytes.h sample.h verify.h owcpa.h kem.h

OBJS = poly_rq_mul.s

all: test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair \
     test/gen_owcpa_vecs

poly_rq_mul.s: asmgen/rq_mul/poly_rq_mul.py asmgen/rq_mul/K2_schoolbook_64x11.py asmgen/rq_mul/K2_K2_64x44.py
	python3 $^ > $@

%.s: asmgen/%.py
	python3 $^ > $@

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
