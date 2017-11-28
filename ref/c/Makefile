CC = /usr/bin/cc
CFLAGS = -Wall -Wextra -Wpedantic -O3

SOURCES = poly.c fips202.c randombytes.c cbd.c verify.c owcpa.c ntrukem.c
HEADERS = params.h poly.h randombytes.h cbd.h verify.h owcpa.h ntrukem.h

all: test/test_poly \
     test/test_polymul \
     test/test_ntru \
     test/test_pack \
     test/test_cshake \
     test/test_shake \
     test/ram \
     test/speed \
     test/encap \
     test/decap \
     test/keypair \
     test/gen_owcpa_vecs \

test/test_polymul: $(SOURCES) $(HEADERS) test/test_polymul.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_polymul.c

test/test_poly: $(SOURCES) $(HEADERS) test/test_poly.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_poly.c

test/test_ntru: $(SOURCES) $(HEADERS) test/test_ntru.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_ntru.c

test/test_pack: $(SOURCES) $(HEADERS) test/test_pack.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) test/test_pack.c

test/speed: $(SOURCES) $(HEADERS) cpucycles.h cpucycles.c test/speed.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) cpucycles.c test/speed.c

test/ram: $(SOURCES) $(OBJS) $(HEADERS) test/ram.c
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(OBJS) test/ram.c

test/test_cshake: fips202.h fips202.c test/test_cshake.c
	$(CC) $(CFLAGS) -o $@ fips202.c test/test_cshake.c

test/test_shake: fips202.h fips202.c test/test_shake.c
	$(CC) $(CFLAGS) -o $@ fips202.c test/test_shake.c

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
	./test/test_poly
	./test/test_polymul
	./test/test_ntru
	./test/test_pack
	./test/test_cshake
	./test/test_shake
	./test/speed
	./test/ram

clean:
	-$(RM) *.o
	-$(RM) -r test/test_poly
	-$(RM) -r test/test_polymul
	-$(RM) -r test/test_ntru
	-$(RM) -r test/test_pack
	-$(RM) -r test/test_cshake
	-$(RM) -r test/test_shake
	-$(RM) -r test/speed
	-$(RM) -r test/encap
	-$(RM) -r test/decap
	-$(RM) -r test/keypair
	-$(RM) -r util/gen_owcpa_vecs
