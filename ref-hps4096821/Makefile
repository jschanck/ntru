CC = /usr/bin/cc
CFLAGS = -Wall -Wextra -Wpedantic -O3

SOURCES = crypto_sort.c poly.c pack3.c packq.c fips202.c randombytes.c sample.c verify.c owcpa.c kem.c
HEADERS = crypto_sort.h params.h poly.h randombytes.h sample.h verify.h owcpa.h kem.h

all: test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair \
     test/gen_owcpa_vecs

test/test_polymul: $(SOURCES) $(HEADERS) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_polymul.c

test/test_ntru: $(SOURCES) $(HEADERS) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_ntru.c

test/test_pack: $(SOURCES) $(HEADERS) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_pack.c

test/speed: $(SOURCES) $(HEADERS) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) cpucycles.c test/speed.c

test/ram: $(SOURCES) $(OBJS) $(HEADERS) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/ram.c

test/gen_owcpa_vecs: test/gen_owcpa_vecs.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/gen_owcpa_vecs.c

test/encap: $(SOURCES) $(HEADERS) test/encap.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/encap.c

test/decap: $(SOURCES) $(HEADERS) test/decap.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/decap.c

test/keypair: $(SOURCES) $(HEADERS) test/keypair.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/keypair.c

.PHONY: clean test

test:
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
	-$(RM) -r test/gen_owcpa_vecs
