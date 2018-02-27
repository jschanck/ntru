## High-speed key encapsulation from NTRU

This code package contains the source code that accompanies the paper _"High-speed key encapsulation from NTRU"_. It contains a C reference implementation and an optimized AVX2 implementation, in the respective directories. When referring to this implementation, please refer to the original publication:

> Andreas Hülsing, Joost Rijneveld, John Schanck, and Peter Schwabe. High-speed key encapsulation from NTRU. _Cryptographic Hardware and Embedded Systems – CHES 2017_, LNCS 10529, pp. 232-252, Springer, 2017. https://joostrijneveld.nl/papers/ntrukem

Note that the source code differs slightly from the NTRU-HRSS-KEM scheme that was submitted to [NIST's Post-Quantum Cryptography project](https://csrc.nist.gov/Projects/Post-Quantum-Cryptography/Round-1-Submissions) in November 2017. The relevant changes have been applied in the `NIST` branch of this repository.
