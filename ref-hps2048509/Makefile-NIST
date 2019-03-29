CC=/usr/bin/gcc
LDFLAGS=-lcrypto

SOURCES = crypto_sort.c fips202.c kem.c owcpa.c pack3.c packq.c poly.c sample.c verify.c rng.c PQCgenKAT_kem.c
HEADERS = api.h crypto_sort.h fips202.h kem.h poly.h owcpa.h params.h sample.h verify.h rng.h

PQCgenKAT_kem: $(HEADERS) $(SOURCES)
	$(CC) -o $@ $(SOURCES) $(LDFLAGS)

.PHONY: clean

clean:
	-rm PQCgenKAT_kem

