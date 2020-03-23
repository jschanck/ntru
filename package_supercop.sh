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

echo "66f43b84ed90c246c40c03904fddd0d6137bc2153829f214038cebe89dd6772f" > checksumsmall
echo "11d99e8437286529ef7db4a7a8dea3524ede2a16bc266c754b9c233eb255c0b3" > checksumbig
)

# special files for hps2048677

(
cd ${DIRNAME}/ntruhps2048677/

for i in "${ONLYHPS677[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048677/$i avx2/$i
done

echo "cedd16c6a222107c57e6fab41a4277ca35816b75f49a9afb951a8bf8f9236e2f" > checksumsmall
echo "1c0b86a65604d7a84d9c7791ab0ad3dbff983f03abda0cd7dae49f57ad77a630" > checksumbig
)

# special files for hps4096821

(
cd ${DIRNAME}/ntruhps4096821/

for i in "${ONLYHPS821[@]}"; do
  cp -l ${WORKDIR}/avx2-hps4096821/$i avx2/$i
done

echo "2ac4d15dffb2f7c317bd5595009d3d553c86107f9ec0164379ca1eb4d1b0c813" > checksumsmall
echo "ed42da97b53d62eb8328379f39806af7df25914d149f31225764de4b7b2dae38" > checksumbig
)

# special files for hrss701

(
cd ${DIRNAME}/ntruhrss701/

for i in "${ONLYHRSS701[@]}"; do
  cp -l ${WORKDIR}/avx2-hrss701/$i avx2/$i
done

echo "95b39b282fe1b91eb4b7bd5957693eaec5cd73e37c25699127d6d87751453cd4" > checksumsmall
echo "50e9bccc8bbc93496ca3a77e9beed329ba18ce5a83a529359b706d16aeda7e14" > checksumbig

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
