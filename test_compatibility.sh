#!/bin/bash

make -C ref-hrss701 {test/keypair,test/encap,test/decap}
make -C avx2-hrss701 {test/keypair,test/encap,test/decap}

PKBYTES=1138
SKBYTES=1450
KEYBYTES=32
BYTES=1138

keyfile=$(mktemp)
ciphertextandkey=$(mktemp)
ciphertext=$(mktemp)
key=$(mktemp)

for keygen in {"ref-hrss701","avx2-hrss701"}; do
    for encap in {"ref-hrss701","avx2-hrss701"}; do
        for decap in {"ref-hrss701","avx2-hrss701"}; do
            echo -n "Testing with keygen: ${keygen}, encap: ${encap}, decap: ${decap}.. "
            ${keygen}/test/keypair > ${keyfile}
            head -c ${PKBYTES} ${keyfile} | ${encap}/test/encap > ${ciphertextandkey}
            head -c ${BYTES} ${ciphertextandkey} > ${ciphertext}
            tail -c ${SKBYTES} ${keyfile} | cat - ${ciphertext} | ${decap}/test/decap > ${key}
            k1sum=$(tail -c ${KEYBYTES} ${ciphertextandkey} | md5sum | cut -f 1 -d' ')
            k2sum=$(md5sum ${key} | cut -f 1 -d' ')
            if [ ${k1sum} == ${k2sum} ]
            then
                echo "succeeded!"
            else
                echo "failed!"
            fi
        done
    done
done

rm ${keyfile}
rm ${ciphertextandkey}
rm ${ciphertext}
rm ${key}





make -C ref-hps2048509 {test/keypair,test/encap,test/decap}
make -C avx2-hps2048509 {test/keypair,test/encap,test/decap}

PKBYTES=699
SKBYTES=935
KEYBYTES=32
BYTES=699

keyfile=$(mktemp)
ciphertextandkey=$(mktemp)
ciphertext=$(mktemp)
key=$(mktemp)

for keygen in {"ref-hps2048509","avx2-hps2048509"}; do
    for encap in {"ref-hps2048509","avx2-hps2048509"}; do
        for decap in {"ref-hps2048509","avx2-hps2048509"}; do
            echo -n "Testing with keygen: ${keygen}, encap: ${encap}, decap: ${decap}.. "
            ${keygen}/test/keypair > ${keyfile}
            head -c ${PKBYTES} ${keyfile} | ${encap}/test/encap > ${ciphertextandkey}
            head -c ${BYTES} ${ciphertextandkey} > ${ciphertext}
            tail -c ${SKBYTES} ${keyfile} | cat - ${ciphertext} | ${decap}/test/decap > ${key}
            k1sum=$(tail -c ${KEYBYTES} ${ciphertextandkey} | md5sum | cut -f 1 -d' ')
            k2sum=$(md5sum ${key} | cut -f 1 -d' ')
            if [ ${k1sum} == ${k2sum} ]
            then
                echo "succeeded!"
            else
                echo "failed!"
            fi
        done
    done
done

rm ${keyfile}
rm ${ciphertextandkey}
rm ${ciphertext}
rm ${key}




make -C ref-hps2048677 {test/keypair,test/encap,test/decap}
make -C avx2-hps2048677 {test/keypair,test/encap,test/decap}

PKBYTES=930
SKBYTES=1234
KEYBYTES=32
BYTES=930


keyfile=$(mktemp)
ciphertextandkey=$(mktemp)
ciphertext=$(mktemp)
key=$(mktemp)

for keygen in {"ref-hps2048677","avx2-hps2048677"}; do
    for encap in {"ref-hps2048677","avx2-hps2048677"}; do
        for decap in {"ref-hps2048677","avx2-hps2048677"}; do
            echo -n "Testing with keygen: ${keygen}, encap: ${encap}, decap: ${decap}.. "
            ${keygen}/test/keypair > ${keyfile}
            head -c ${PKBYTES} ${keyfile} | ${encap}/test/encap > ${ciphertextandkey}
            head -c ${BYTES} ${ciphertextandkey} > ${ciphertext}
            tail -c ${SKBYTES} ${keyfile} | cat - ${ciphertext} | ${decap}/test/decap > ${key}
            k1sum=$(tail -c ${KEYBYTES} ${ciphertextandkey} | md5sum | cut -f 1 -d' ')
            k2sum=$(md5sum ${key} | cut -f 1 -d' ')
            if [ ${k1sum} == ${k2sum} ]
            then
                echo "succeeded!"
            else
                echo "failed!"
            fi
        done
    done
done

rm ${keyfile}
rm ${ciphertextandkey}
rm ${ciphertext}
rm ${key}




make -C ref-hps4096821 {test/keypair,test/encap,test/decap}
make -C avx2-hps4096821 {test/keypair,test/encap,test/decap}

PKBYTES=1230
SKBYTES=1590
KEYBYTES=32
BYTES=1230

keyfile=$(mktemp)
ciphertextandkey=$(mktemp)
ciphertext=$(mktemp)
key=$(mktemp)

for keygen in {"ref-hps4096821","avx2-hps4096821"}; do
    for encap in {"ref-hps4096821","avx2-hps4096821"}; do
        for decap in {"ref-hps4096821","avx2-hps4096821"}; do
            echo -n "Testing with keygen: ${keygen}, encap: ${encap}, decap: ${decap}.. "
            ${keygen}/test/keypair > ${keyfile}
            head -c ${PKBYTES} ${keyfile} | ${encap}/test/encap > ${ciphertextandkey}
            head -c ${BYTES} ${ciphertextandkey} > ${ciphertext}
            tail -c ${SKBYTES} ${keyfile} | cat - ${ciphertext} | ${decap}/test/decap > ${key}
            k1sum=$(tail -c ${KEYBYTES} ${ciphertextandkey} | md5sum | cut -f 1 -d' ')
            k2sum=$(md5sum ${key} | cut -f 1 -d' ')
            if [ ${k1sum} == ${k2sum} ]
            then
                echo "succeeded!"
            else
                echo "failed!"
            fi
        done
    done
done

rm ${keyfile}
rm ${ciphertextandkey}
rm ${ciphertext}
rm ${key}
