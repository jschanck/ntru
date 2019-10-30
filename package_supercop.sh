#!/bin/bash

WORKDIR=`dirname $0`
WORKDIR=`cd $WORKDIR && pwd`
echo $WORKDIR

DIRNAME=${WORKDIR}/crypto_kem

ALL=(
  kem.h
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
  poly_rq_mul.c
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
mkdir -p ${DIRNAME}/ntruhrss701/ref

mkdir -p ${DIRNAME}/ntruhps2048509/avx2
mkdir -p ${DIRNAME}/ntruhps2048509/ref

mkdir -p ${DIRNAME}/ntruhps2048677/avx2
mkdir -p ${DIRNAME}/ntruhps2048677/ref

mkdir -p ${DIRNAME}/ntruhps4096821/avx2
mkdir -p ${DIRNAME}/ntruhps4096821/ref


for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do

  ( cd ${WORKDIR}/avx2-${PARAM} && make asm )

  ( cd ${DIRNAME}/ntru${PARAM}/

  echo "#include \"crypto_kem.h\"" >  ref/kem.c
  cat ${WORKDIR}/ref-${PARAM}/kem.c >> ref/kem.c

  ln -s ../ref/kem.c avx2/kem.c

  for i in "${ALL[@]}"; do
    cp -l ${WORKDIR}/ref-${PARAM}/$i ref/$i
    ( cd avx2 && ln -s ../ref/$i $i )
  done

  for i in "${ONLYREF[@]}"; do
    cp -l ${WORKDIR}/ref-${PARAM}/$i ref/$i
  done

  cp ${WORKDIR}/avx2-${PARAM}/*.s avx2/

  touch goal-indcca2 goal-indcpa nistpqc nistpqc1 nistpqc2

  echo "ntru${PARAM} as specified by the NTRU submission to the second round of the NIST post-quantum standardisation process." > description
  echo "Cong Chen
Oussama Danba
Jeffrey Hoffstein
Andreas Hülsing
Joost Rijneveld
John M. Schanck
Peter Schwabe
William Whyte
Zhenfei Zhang" > designers

  echo "Oussama Danba
Joost Rijneveld
John M. Schanck
Peter Schwabe" > ref/implementors
  cp ref/implementors avx2/implementors

  echo "amd64
x86" > avx2/architectures

  cp ${WORKDIR}/avx2-${PARAM}/api_bytes.h ref/api.h
  cp ${WORKDIR}/avx2-${PARAM}/api_bytes.h avx2/api.h
  )

done

# special files for hps2048509

(
cd ${DIRNAME}/ntruhps2048509/

for i in "${ONLYHPS509[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048509/$i avx2/$i
done

echo "057b9853c1d5afbcde8c674dee733baccf112f0d3bda75e99c0465733bd15c91" > checksumbig
echo "a069c6ac317d509349e9828723e4ce2beee879abee32a76f938bc2008b3928b2" > checksumsmall
)

# special files for hps2048677

(
cd ${DIRNAME}/ntruhps2048677/

for i in "${ONLYHPS677[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048677/$i avx2/$i
done

echo "203b1d763ebdca2620eabac6b0111a8c281101a61c1f849debefaef02dec25d4" > checksumbig
echo "c4249772037609c251c1cf90e18de5e99b9a08838441e59b75c6962f6710ae38" > checksumsmall
)

# special files for hps4096821

(
cd ${DIRNAME}/ntruhps4096821/

for i in "${ONLYHPS821[@]}"; do
  cp -l ${WORKDIR}/avx2-hps4096821/$i avx2/$i
done

echo "596acc49c4d10836755d96b5095566b45d6ca3f18812c7b02aed9b2d0e092878" > checksumbig
echo "e37343c3fea69ad913549a550cfb9221b3058abb1c0d1f479ea94c116195c497" > checksumsmall
)

# special files for hrss701

(
cd ${DIRNAME}/ntruhrss701/

for i in "${ONLYHRSS701[@]}"; do
  cp -l ${WORKDIR}/avx2-hrss701/$i avx2/$i
done

echo "e18d70bd4c1001c6fb6cb690159053c9277bdd9593dd9e02a58b981ba594a2ae" > checksumbig
echo "532a32f821b8b1d607f82fbe34ced3110d10ba2ad7ce4bd17c1dea425ab9631d" > checksumsmall

rm avx2/poly_s3_inv.s
cat > avx2/poly_s3_inv.c <<herefiledelim
#include "poly.h"
#include "crypto_core_invhrss701.h"

void poly_S3_inv(poly *r, const poly *a)
{
  crypto_core_invhrss701((void *) r,(const void *) a,0,0);
}
herefiledelim
)

tar czf supercop-ntru-$(date +"%Y%m%d").tar.gz crypto_kem/
rm -rf crypto_kem
