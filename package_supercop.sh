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
  mkdir -p ${DIRNAME}/ntru${PARAM}/ref

  #TODO: Longterm namespacing solution. SUPERCOP does not guarantee
  #      the "_avx2_constbranchindex" suffix.
  export NTRU_NAMESPACE=crypto_kem_ntru${PARAM}_avx2_constbranchindex_
  ( cd ${WORKDIR}/avx2-${PARAM} && make -B asm )

  ( cd ${WORKDIR}/ref-${PARAM}/
    cp -l api_bytes.h ${DIRNAME}/ntru${PARAM}/ref/api.h
    cp -l cmov.h owcpa.h kem.h params.h poly.h sample.h ${DIRNAME}/ntru${PARAM}/ref/
    cp -l cmov.c kem.c owcpa.c pack3.c packq.c poly.c poly_lift.c poly_mod.c poly_r2_inv.c poly_rq_mul.c poly_s3_inv.c sample.c sample_iid.c ${DIRNAME}/ntru${PARAM}/ref/ )

  ( cd ${WORKDIR}/avx2-${PARAM}/
    cp -l api_bytes.h ${DIRNAME}/ntru${PARAM}/avx2/api.h
    cp -l cmov.h owcpa.h kem.h params.h poly.h poly_r2_inv.h sample.h ${DIRNAME}/ntru${PARAM}/avx2/
    cp -l cmov.c kem.c owcpa.c pack3.c packq.c poly.c poly_r2_inv.c sample.c sample_iid.c ${DIRNAME}/ntru${PARAM}/avx2/
    cp -l *.s ${DIRNAME}/ntru${PARAM}/avx2/ )

  ( cd ${WORKDIR}/avx2-${PARAM}/
  if [ "${PARAM}" != "hrss701" ]; then
      cp -l poly_lift.c poly_s3_inv.c ${DIRNAME}/ntru${PARAM}/avx2/
  fi )

  ( cd ${DIRNAME}/ntru${PARAM}
  touch goal-indcca2 goal-indcpa nistpqc nistpqc1 nistpqc2 nistpqc3
  touch ref/goal-constbranch ref/goal-constindex
  touch avx2/goal-constbranch avx2/goal-constindex

  echo "ntru${PARAM} as specified by the NTRU submission to the second round of the NIST post-quantum standardisation process." > description
  echo "Cong Chen
Oussama Danba
Jeffrey Hoffstein
Andreas Hülsing
Joost Rijneveld
Tsunekazu Saito
John M. Schanck
Peter Schwabe
William Whyte
Keita Xagawa
Takashi Yamakawa
Zhenfei Zhang" > designers

  echo "Oussama Danba
Joost Rijneveld
John M. Schanck
Peter Schwabe" > ref/implementors
  cp ref/implementors avx2/implementors

  echo "amd64
x86" > avx2/architectures )
done

# special files for hps2048509

(
cd ${DIRNAME}/ntruhps2048509/

for i in "${ONLYAVX2_HPS[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048509/$i avx2/$i
done

echo "00cd3fe1b21cd7ad209de97d76eba108e51415ad7ed1fd717df6c7bcf4135c06" > checksumsmall
echo "7034d970bde4229b59bee12a892dc555b9c20ace10fa95871d647553a89da00c" > checksumbig
)

# special files for hps2048677

(
cd ${DIRNAME}/ntruhps2048677/

for i in "${ONLYAVX2_HPS[@]}"; do
  cp -l ${WORKDIR}/avx2-hps2048677/$i avx2/$i
done

echo "2235d41f90f9ea218486529e8385ee98fa0680e2c8c80aa2690c08e44e102db5" > checksumsmall
echo "c2e84c441cc7b06b9075e3f010acbe9af8ed6f62de8e913fdf00daac9dccd96c" > checksumbig
)

# special files for hps4096821

(
cd ${DIRNAME}/ntruhps4096821/

for i in "${ONLYAVX2_HPS[@]}"; do
  cp -l ${WORKDIR}/avx2-hps4096821/$i avx2/$i
done

echo "202e8de9cd4dc0446643f740cb4fc9d5b8effd5f8fded33b6d4fc6d022bce04a" > checksumsmall
echo "ba7975339f1f65b53a6610d6e9dcddee7b337cf2188bcf0114bde0ec8dfd5f70" > checksumbig
)

# special files for hrss701

(
cd ${DIRNAME}/ntruhrss701/

for i in "${ONLYAVX2_HRSS[@]}"; do
  cp -l ${WORKDIR}/avx2-hrss701/$i avx2/$i
done

echo "e81768c877922de14d035615ad7695b679f4a634f58516b40c1c25f6a6ddef3a" > checksumsmall
echo "f905d7d93153a42169d0b2d9e7ebf5b91b706229c05c0ef53a01dd2fa6c06b2e" > checksumbig

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


# TIMECOP


for PARAM in hrss701 hps2048509 hps2048677 hps4096821; do
  for IMPL in ref avx2; do
  (
    cd ${DIRNAME}/ntru${PARAM}/${IMPL}
    echo "\
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} gcc_-march=native_-mtune=native_-O3_-fomit-frame-pointer_-fwrapv_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} gcc_-march=native_-mtune=native_-Os_-fomit-frame-pointer_-fwrapv_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} gcc_-march=native_-mtune=native_-O2_-fomit-frame-pointer_-fwrapv_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} gcc_-march=native_-mtune=native_-O_-fomit-frame-pointer_-fwrapv_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} clang_-march=native_-O3_-fomit-frame-pointer_-fwrapv_-Qunused-arguments_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} clang_-march=native_-Os_-fomit-frame-pointer_-fwrapv_-Qunused-arguments_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} clang_-march=native_-O2_-fomit-frame-pointer_-fwrapv_-Qunused-arguments_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} clang_-march=native_-O_-fomit-frame-pointer_-fwrapv_-Qunused-arguments_-fPIC_-fPIE 3 0
    20200816 koko amd64 20200821 crypto_kem ntru${PARAM}/constbranchindex timecop_pass crypto_kem/ntru${PARAM}/${IMPL} clang_-mcpu=native_-O3_-fomit-frame-pointer_-fwrapv_-Qunused-arguments_-fPIC_-fPIE 3 0" \
      > goal-constbranch
    cp goal-constbranch goal-constindex
  )
  done
done

tar czf supercop-ntru-$(date +"%Y%m%d").tar.gz crypto_kem/
rm -rf ${DIRNAME}
