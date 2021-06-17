all: ref avx2

ref:  ref-hrss701 \
      ref-hrss1373 \
      ref-hps2048509 \
      ref-hps2048677 \
      ref-hps4096821 \
      ref-hps40961229

avx2: avx2-hrss701 \
      avx2-hps2048509 \
      avx2-hps2048677 \
      avx2-hps4096821

ref-%:
	$(MAKE) -C ../$@/ -f Makefile-NIST
	mkdir -p ref && cd ref && ../../$@/PQCgenKAT_kem

avx2-%:
	$(MAKE) -C ../$@/ -f Makefile-NIST
	mkdir -p avx2 && cd avx2 && ../../$@/PQCgenKAT_kem

