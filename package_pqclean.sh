#!/bin/bash


WORKDIR=`dirname $0`
WORKDIR=`cd $WORKDIR && pwd`
echo $WORKDIR

DIRNAME=${WORKDIR}/crypto_kem

ALL=(
  api.h
  kem.c
  owcpa.c
  owcpa.h
  pack3.c
  packq.c
  params.h
  poly.c
  poly.h
  sample.c
  sample.h
  sample_iid.c
  verify.c
  verify.h
)

ONLYREF=(
  poly_mod.c
  poly_lift.c
  poly_r2_inv.c
  poly_s3_inv.c
  poly_rq_mul.c
)

ONLYHPS509=(
  poly_lift.c
  poly_s3_inv.c
  poly_r2_inv.c
  poly_r2_inv.h
)

ONLYHPS677=(
  poly_lift.c
  poly_s3_inv.c
  poly_r2_inv.c
  poly_r2_inv.h
)

ONLYHPS821=(
  poly_lift.c
  poly_s3_inv.c
  poly_r2_inv.c
  poly_r2_inv.h
)

ONLYHRSS701=(
  poly_r2_inv.c
  poly_r2_inv.h
)

cd $WORKDIR

if [ -e "$DIRNAME" ]; then
  echo "Error; directory already exists; delete first."
  exit -1
fi

mkdir -p ${DIRNAME}/ntruhrss701/avx2
mkdir -p ${DIRNAME}/ntruhrss701/clean

mkdir -p ${DIRNAME}/ntruhps2048509/avx2
mkdir -p ${DIRNAME}/ntruhps2048509/clean

mkdir -p ${DIRNAME}/ntruhps2048677/avx2
mkdir -p ${DIRNAME}/ntruhps2048677/clean

mkdir -p ${DIRNAME}/ntruhps4096821/avx2
mkdir -p ${DIRNAME}/ntruhps4096821/clean

for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do

  export NTRU_NAMESPACE=PQCLEAN_NTRU${PARAM^^}_AVX2_
  ( cd ${WORKDIR}/avx2-${PARAM} && make clean && make asm )

  ( cd ${DIRNAME}/ntru${PARAM}/

  for i in "${ALL[@]}"; do
    cp -l ${WORKDIR}/ref-${PARAM}/$i clean/$i
    cp -l ${WORKDIR}/avx2-${PARAM}/$i avx2/$i
  done

  for i in "${ONLYREF[@]}"; do
    cp -l ${WORKDIR}/ref-${PARAM}/$i clean/$i
  done

  cp ${WORKDIR}/avx2-${PARAM}/*.s avx2/
)
done

# special files for hps2048509

(
cd ${DIRNAME}/ntruhps2048509/

for i in "${ONLYHPS509[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048509/$i avx2/$i
done
)

# special files for hps2048677

(
cd ${DIRNAME}/ntruhps2048677/

for i in "${ONLYHPS677[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048677/$i avx2/$i
done
)

# special files for hps4096821

(
cd ${DIRNAME}/ntruhps4096821/

for i in "${ONLYHPS821[@]}"; do
  cp -l ${WORKDIR}/avx2-hps4096821/$i avx2/$i
done
)

# special files for hrss701

(
cd ${DIRNAME}/ntruhrss701/

for i in "${ONLYHRSS701[@]}"; do
  cp -l ${WORKDIR}/avx2-hrss701/$i avx2/$i
done
)

# Makefiles and other metadata
for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do

  ( cd ${DIRNAME}/ntru${PARAM}/
  echo "Public Domain" > clean/LICENSE
  cp clean/LICENSE avx2/LICENSE

  echo \
"# This Makefile can be used with GNU Make or BSD Make

LIB=libntru${PARAM}_clean.a
HEADERS=$(basename -a clean/*.h | tr '\n' ' ')
OBJECTS=$(basename -a clean/*.c | sed 's/\.c/.o/' | tr '\n' ' ')

CFLAGS=-O3 -Wall -Wextra -Wpedantic -Werror -Wmissing-prototypes -Wredundant-decls -std=c99 -I../../../common \$(EXTRAFLAGS)

all: \$(LIB)

%.o: %.c \$(HEADERS)
	\$(CC) \$(CFLAGS) -c -o \$@ $<

\$(LIB): \$(OBJECTS)
	\$(AR) -r \$@ \$(OBJECTS)

clean:
	\$(RM) \$(OBJECTS)
	\$(RM) \$(LIB)" > clean/Makefile

  echo \
"# This Makefile can be used with Microsoft Visual Studio's nmake using the command:
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


  echo \
"# This Makefile can be used with GNU Make or BSD Make

LIB=libntru${PARAM}_avx2.a
HEADERS=$(basename -a avx2/*.h | tr '\n' ' ')
OBJECTS=$(basename -a avx2/*.c | sed 's/\.c/.o/' | tr '\n' ' ') \\
        $(basename -a avx2/square_* | sort -V | sed 's/\.s/.o/' | tr '\n' ' ') \\
        $(basename -a avx2/poly_*.s | sed 's/\.s/.o/' | tr '\n' ' ') vec32_sample_iid.o

CFLAGS=-O3 -mavx2 -mbmi2 -Wall -Wextra -Wpedantic -Werror -Wmissing-prototypes -Wredundant-decls -std=c99 -I../../../common \$(EXTRAFLAGS)

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

# Simplify ifdefs
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/0/" ${DIRNAME}/ntruhrss701/*/pack3.c
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/1/" ${DIRNAME}/ntruhps2048509/*/pack3.c
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/1/" ${DIRNAME}/ntruhps2048677/*/pack3.c
sed -i -s "s/NTRU_PACK_DEG > (NTRU_PACK_DEG \/ 5) \* 5/0/" ${DIRNAME}/ntruhps4096821/*/pack3.c
sed -i -s "s/(NTRU_N - 1) > ((NTRU_N - 1) \/ 4) \* 4/0/" ${DIRNAME}/ntruhrss701/*/sample.c
sed -i -s "s/(NTRU_N - 1) > ((NTRU_N - 1) \/ 4) \* 4/0/" ${DIRNAME}/ntruhps2048509/*/sample.c
sed -i -s "s/(NTRU_N - 1) > ((NTRU_N - 1) \/ 4) \* 4/0/" ${DIRNAME}/ntruhps2048677/*/sample.c
sed -i -s "s/(NTRU_N - 1) > ((NTRU_N - 1) \/ 4) \* 4/0/" ${DIRNAME}/ntruhps4096821/*/sample.c

unifdef -k -m -UNTRU_HPS -DNTRU_HRSS -DNTRU_N=701 -DNTRU_Q=8192 ${DIRNAME}/ntruhrss701/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=509 -DNTRU_Q=2048 ${DIRNAME}/ntruhps2048509/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=677 -DNTRU_Q=2048 ${DIRNAME}/ntruhps2048677/*/*.{c,h}
unifdef -k -m -DNTRU_HPS -UNTRU_HRSS -DNTRU_N=821 -DNTRU_Q=4096 ${DIRNAME}/ntruhps4096821/*/*.{c,h}

# Replace unsigned char with uint8_t at top level

sed -i -s "s/unsigned char /uint8_t /g" ${DIRNAME}/*/*/api.h
sed -i -s "s/unsigned char /uint8_t /g" ${DIRNAME}/*/*/kem.c
sed -i -s "3a#include <stdint.h>\n" ${DIRNAME}/*/*/api.h

# Replace crypto_hash_sha3_256 with sha3_256

sed -i -s "s/crypto_hash_sha3256\.h/fips202.h/g" ${DIRNAME}/*/*/kem.c
sed -i -s "s/crypto_hash_sha3256/sha3_256/g" ${DIRNAME}/*/*/kem.c


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

# Manual namespacing of C files

NEEDS_NAMESPACE=(
  API_H
  CRYPTO_
  cmov
  crypto_kem_
  owcpa_
  poly_
  sample_
  square_
  vec32_sample_
  verify
)

for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do
  NTRU_NAMESPACE=PQCLEAN_NTRU${PARAM^^}_CLEAN_
  for X in ${NEEDS_NAMESPACE[@]}; do
    sed -i -s "s/ ${X}/ ${NTRU_NAMESPACE}${X}/g" ${DIRNAME}/ntru${PARAM}/clean/*.c ${DIRNAME}/ntru${PARAM}/clean/*.h
  done
done

for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do
  NTRU_NAMESPACE=PQCLEAN_NTRU${PARAM^^}_AVX2_
  for X in ${NEEDS_NAMESPACE[@]}; do
    sed -i -s "s/ ${X}/ ${NTRU_NAMESPACE}${X}/g" ${DIRNAME}/ntru${PARAM}/avx2/*.c ${DIRNAME}/ntru${PARAM}/avx2/*.h
  done
done

tar czf pqclean-ntru-$(date +"%Y%m%d").tar.gz crypto_kem/
rm -rf ${DIRNAME}
