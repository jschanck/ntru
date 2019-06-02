import unittest
import squaring_mod_GF2N as sqGF2N
from bitpermutations.data import Register, MemoryFragment, ZERO
from bitpermutations.utils import sequence_to_values


class TestSquaringModGF2N_patience(unittest.TestCase):

    def test_square_509_patience(self):
        src = [MemoryFragment(64, '{}(%rsi)'.format(i*8))for i in range(8)]
        dst = [MemoryFragment(64, '{}(%rdi)'.format(i*8)) for i in range(8)]
        for n in range(10):
            seq = sqGF2N.gen_sequence(n, 509)
            sequence_to_values(src, range(0, 509), padding=ZERO)

            sqGF2N.square_509_patience(dst, src, n)
            result = sqGF2N.registers_to_sequence(dst)

            if self.assertEqual(result, seq):
                break

    def test_square_509_patience_callee_save(self):
        src = [MemoryFragment(64, '{}(%rsi)'.format(i*8))for i in range(8)]
        dst = [MemoryFragment(64, '{}(%rdi)'.format(i*8)) for i in range(8)]
        seq = sqGF2N.gen_sequence(5, 509)
        sequence_to_values(src, range(0, 509), padding=ZERO)

        sqGF2N.square_509_patience(dst, src, 5, 5)
        result = sqGF2N.registers_to_sequence(dst)

        self.assertEqual(result, seq)


class TestSquaringModGF2N_permutations(unittest.TestCase):

    def test_square_509_shufbytes(self):
        src = [MemoryFragment(256, '{}(%rsi)'.format(i*32)) for i in range(2)]
        dst = [MemoryFragment(256, '{}(%rdi)'.format(i*32)) for i in range(2)]

        for n in [1, 3, 6, 15, 30, 63, 126, 252]:
            seq = sqGF2N.gen_sequence(n, 509)
            sequence_to_values(src, range(0, 509), padding=ZERO)

            sqGF2N.square_509_shufbytes(dst, src, n)
            result = sqGF2N.registers_to_sequence(dst)

            if self.assertEqual(result, seq):
                break


if __name__ == '__main__':
    unittest.main()
