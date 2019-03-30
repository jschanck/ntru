CC = /usr/bin/cc
CFLAGS = -O3 -fomit-frame-pointer -march=native -no-pie
LDFLAGS=-lcrypto

SOURCES = poly.c pack3.c packq.c fips202.c sample.c verify.c owcpa.c kem.c poly_r2_inv.c rng.c PQCgenKAT_kem.c \
					square_1_701_patience.s \
					square_3_701_patience.s \
					square_6_701_patience.s \
					square_12_701_shufbytes.s \
					square_15_701_shufbytes.s \
					square_27_701_shufbytes.s \
					square_42_701_shufbytes.s \
					square_84_701_shufbytes.s \
					square_168_701_shufbytes.s \
					square_336_701_shufbytes.s \
					poly_r2_mul.s  \
					poly_rq_mul.s  \
					poly_s3_mul.s  \
					poly_rq_mul_x_minus_1.s \
					poly_s3_inv.s  \
					poly_rq_to_s3.s  \
					poly_s3_to_rq.s

HEADERS = params.h poly.h sample.h verify.h owcpa.h kem.h poly_r2_inv.h rng.h api.h

PQCgenKAT_kem: $(HEADERS) $(SOURCES)
	$(CC) $(CFLAGS) -o $@ $(SOURCES) $(LDFLAGS)

.PHONY: clean

clean:
	-rm PQCgenKAT_kem

