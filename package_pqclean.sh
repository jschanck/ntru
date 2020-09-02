#!/bin/bash

WORKDIR=`dirname $0`
WORKDIR=`cd $WORKDIR && pwd`
VERSION=$(git rev-parse HEAD)
echo $WORKDIR

DIRNAME=${WORKDIR}/crypto_kem

if [ -e "$DIRNAME" ]; then
  echo "Error; directory already exists; delete first."
  exit -1
fi

for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do
  mkdir -p ${DIRNAME}/ntru${PARAM}/avx2
  mkdir -p ${DIRNAME}/ntru${PARAM}/clean

  export NTRU_NAMESPACE=$(echo PQCLEAN_NTRU${PARAM}_AVX2_ | tr [:lower:] [:upper:])
  ( cd ${WORKDIR}/avx2-${PARAM} && make -B asm )

  ( cd ${WORKDIR}/ref-${PARAM}/
    cp -Lp api.h cmov.h owcpa.h params.h poly.h sample.h ${DIRNAME}/ntru${PARAM}/clean/
    cp -Lp cmov.c kem.c owcpa.c pack3.c packq.c poly.c poly_lift.c poly_mod.c poly_r2_inv.c poly_rq_mul.c poly_s3_inv.c sample.c sample_iid.c ${DIRNAME}/ntru${PARAM}/clean/ )

  ( cd ${WORKDIR}/avx2-${PARAM}/
    cp -Lp api.h cmov.h owcpa.h params.h poly.h poly_r2_inv.h sample.h ${DIRNAME}/ntru${PARAM}/avx2/
    cp -Lp cmov.c kem.c owcpa.c pack3.c packq.c poly.c poly_r2_inv.c sample.c sample_iid.c ${DIRNAME}/ntru${PARAM}/avx2/
    cp -Lp *.s ${DIRNAME}/ntru${PARAM}/avx2/ )

  if [ "${PARAM}" != "hrss701" ]; then
    ( cd ${WORKDIR}/ref-${PARAM}/
      cp -Lp crypto_sort_int32.h ${DIRNAME}/ntru${PARAM}/clean/
      cp -Lp crypto_sort_int32.c ${DIRNAME}/ntru${PARAM}/clean/ )

    ( cd ${WORKDIR}/avx2-${PARAM}/
      cp -Lp crypto_sort_int32.h ${DIRNAME}/ntru${PARAM}/avx2/
      cp -Lp crypto_sort_int32.c poly_lift.c poly_s3_inv.c ${DIRNAME}/ntru${PARAM}/avx2/ )
  fi

# Makefiles and other metadata
( cd ${DIRNAME}/ntru${PARAM}/
echo "Public Domain" > clean/LICENSE
cp clean/LICENSE avx2/LICENSE

echo "\
# This Makefile can be used with GNU Make or BSD Make

LIB=libntru${PARAM}_clean.a
HEADERS=$(basename -a clean/*.h | tr '\n' ' ')
OBJECTS=$(basename -a clean/*.c | sed 's/\.c/.o/' | tr '\n' ' ')

CFLAGS=-O3 -Wall -Wextra -Wpedantic -Wvla -Werror -Wredundant-decls -Wmissing-prototypes -std=c99 -I../../../common \$(EXTRAFLAGS)

all: \$(LIB)

%.o: %.c \$(HEADERS)
	\$(CC) \$(CFLAGS) -c -o \$@ $<

\$(LIB): \$(OBJECTS)
	\$(AR) -r \$@ \$(OBJECTS)

clean:
	\$(RM) \$(OBJECTS)
	\$(RM) \$(LIB)" > clean/Makefile

echo "\
# This Makefile can be used with Microsoft Visual Studio's nmake using the command:
#    nmake /f Makefile.Microsoft_nmake

LIBRARY=libntru${PARAM}_clean.lib
OBJECTS=$(basename -a clean/*.c | sed 's/\.c/.obj/' | tr '\n' ' ')

CFLAGS=/nologo /O2 /I ..\..\..\common /W4 /WX

all: \$(LIBRARY)

# Make sure objects are recompiled if headers change.
\$(OBJECTS): *.h

\$(LIBRARY): \$(OBJECTS)
    LIB.EXE /NOLOGO /WX /OUT:\$@ \$**

clean:
    -DEL \$(OBJECTS)
    -DEL \$(LIBRARY)" > clean/Makefile.Microsoft_nmake

echo "\
# This Makefile can be used with GNU Make or BSD Make

LIB=libntru${PARAM}_avx2.a
HEADERS=$(basename -a avx2/*.h | tr '\n' ' ')
OBJECTS=$(basename -a avx2/*.c | sed 's/\.c/.o/' | tr '\n' ' ') \\
        $(basename -a avx2/square_* | sort -V | sed 's/\.s/.o/' | tr '\n' ' ') \\
        $(basename -a avx2/poly_*.s | sed 's/\.s/.o/' | tr '\n' ' ') vec32_sample_iid.o

CFLAGS=-O3 -mavx2 -mbmi2 -Wall -Wextra -Wpedantic -Wvla -Werror -Wredundant-decls -Wmissing-prototypes -std=c99 -I../../../common \$(EXTRAFLAGS)

all: \$(LIB)

%.o: %.s \$(HEADERS)
	\$(AS) -o \$@ $<

%.o: %.c \$(HEADERS)
	\$(CC) \$(CFLAGS) -c -o \$@ $<

\$(LIB): \$(OBJECTS)
	\$(AR) -r \$@ \$(OBJECTS)

clean:
	\$(RM) \$(OBJECTS)
	\$(RM) \$(LIB)" > avx2/Makefile
 )
done

echo "\
name: ntruhps2048509
type: kem
claimed-nist-level: 1
claimed-security: IND-CCA2
length-public-key: 699
length-secret-key: 935
length-ciphertext: 699
length-shared-secret: 32
nistkat-sha256: 7ecb93dbc7a588878691f2b2d656ebc42192779f335e3a96197f4ce2134f72c6" \
> ${DIRNAME}/ntruhps2048509/META.yml

echo "\
name: ntruhps2048677
type: kem
claimed-nist-level: 3
claimed-security: IND-CCA2
length-public-key: 930
length-secret-key: 1234
length-ciphertext: 930
length-shared-secret: 32
nistkat-sha256: 715a5caf1ee22bb4b75ff6b10f911fec77e0d63378ea359c0773ee0a4c6cbb97" \
> ${DIRNAME}/ntruhps2048677/META.yml

echo "\
name: ntruhps4096821
type: kem
claimed-nist-level: 5
claimed-security: IND-CCA2
length-public-key: 1230
length-secret-key: 1590
length-ciphertext: 1230
length-shared-secret: 32
nistkat-sha256: 0c5b6b159fab6eb677da469ec35aaa7e6b16162b315dcdb55a3b5da857e10519" \
> ${DIRNAME}/ntruhps4096821/META.yml

echo "\
name: ntruhrss701
type: kem
claimed-nist-level: 3
claimed-security: IND-CCA2
length-public-key: 1138
length-secret-key: 1450
length-ciphertext: 1138
length-shared-secret: 32
nistkat-sha256: 501e000c3eb374ffbfb81b0f16673a6282116465936608d7d164b05635e769e8" \
> ${DIRNAME}/ntruhrss701/META.yml

echo "\
principal-submitters:
  - John M. Schanck
auxiliary-submitters:
  - Cong Chen
  - Oussama Danba
  - Jeffrey Hoffstein
  - Andreas Hülsing
  - Joost Rijneveld
  - Tsunekazu Saito
  - Peter Schwabe
  - William Whyte
  - Keita Xagawa
  - Takashi Yamakawa
  - Zhenfei Zhang
implementations:
    - name: clean
      version: https://github.com/jschanck/ntru/tree/${VERSION:0:8} reference implementation
    - name: avx2
      version: https://github.com/jschanck/ntru/tree/${VERSION:0:8} avx2 implementation
      supported_platforms:
          - architecture: x86_64
            operating_systems:
                - Linux
                - Darwin
            required_flags:
                - avx2
                - bmi2" \
  | tee -a ${DIRNAME}/*/META.yml >/dev/null

# Simplify ifdefs
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/0/" ${DIRNAME}/ntru{hrss701,hps4096821}/*/pack3.c
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/1/" ${DIRNAME}/ntru{hps2048509,hps2048677}/*/pack3.c
sed -i -s "s/(NTRU_N - 1) > ((NTRU_N - 1) \/ 4) \* 4/0/" ${DIRNAME}/ntru*/*/sample.c

unifdef -k -m -DCRYPTO_NAMESPACE ${DIRNAME}/ntru*/*/params.h
unifdef -k -m -UNTRU_HPS -DNTRU_HRSS -DNTRU_N=701 -DNTRU_Q=8192 ${DIRNAME}/ntruhrss701/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=509 -DNTRU_Q=2048 ${DIRNAME}/ntruhps2048509/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=677 -DNTRU_Q=2048 ${DIRNAME}/ntruhps2048677/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=821 -DNTRU_Q=4096 ${DIRNAME}/ntruhps4096821/*/*.{c,h}

# Remove __attribute__ from crypto_sort_int32.c
sed -i -s 's/__attribute__((noinline))//' ${DIRNAME}/*/avx2/crypto_sort_int32.c

# Replace unsigned char with uint8_t at top level
sed -i -s "s/unsigned char /uint8_t /g" ${DIRNAME}/*/*/api.h
sed -i -s "s/unsigned char /uint8_t /g" ${DIRNAME}/*/*/kem.c
sed -i -s "3a#include <stdint.h>\n" ${DIRNAME}/*/*/api.h

# Replace crypto_hash_sha3_256 with sha3_256
sed -i -s "s/crypto_hash_sha3256\.h/fips202.h/g" ${DIRNAME}/*/*/kem.c
sed -i -s "s/crypto_hash_sha3256/sha3_256/g" ${DIRNAME}/*/*/kem.c

# Manual namespacing
for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do
  for IMPL in clean avx2; do
    ( cd ${DIRNAME}/ntru${PARAM}/${IMPL}
    NTRU_NAMESPACE=$(echo PQCLEAN_NTRU${PARAM}_${IMPL}_ | tr [:lower:] [:upper])
    for X in $(grep CRYPTO_NAMESPACE *.{c,h} | cut -f2 -d' ' | sort -u); do
      sed -i -s "s/ ${X}/ ${NTRU_NAMESPACE}${X}/g" *.c *.h
    done
    sed -i -s '/CRYPTO_NAMESPACE/d' *.{c,h}
    sed -i -s '/kem\.h/d' kem.c
    sed -i "s/API_H/${NTRU_NAMESPACE}API_H/" api.h
    sed -i "s/CRYPTO_/${NTRU_NAMESPACE}CRYPTO_/" api.h )
  done
done

# Apply PQClean formatting 
astyle \
  --style=google \
  --indent=spaces \
  --indent-preproc-define \
  --indent-preproc-cond \
  --pad-oper \
  --pad-comma \
  --pad-header \
  --align-pointer=name \
  --add-braces \
  --convert-tabs \
  --mode=c \
  --suffix=none \
  ${DIRNAME}/*/*/*.{c,h}

# Package
tar czf pqclean-ntru-$(date +"%Y%m%d").tar.gz crypto_kem/

# Cleanup
rm -rf ${DIRNAME}
