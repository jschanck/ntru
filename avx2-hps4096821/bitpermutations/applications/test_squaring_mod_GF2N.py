import unittest
import squaring_mod_GF2N as sqGF2N
from bitpermutations.data import Register, MemoryFragment, ZERO
from bitpermutations.utils import sequence_to_values


class TestSquaringModGF2N_patience(unittest.TestCase):

    def test_square_821_patience(self):
        src = [MemoryFragment(64, '{}(%rsi)'.format(i*8))for i in range(16)]
        dst = [MemoryFragment(64, '{}(%rdi)'.format(i*8)) for i in range(16)]
        for n in range(10):
            seq = sqGF2N.gen_sequence(n, 821)
            sequence_to_values(src, range(0, 821), padding=ZERO)

            sqGF2N.square_821_patience(dst, src, n)
            result = sqGF2N.registers_to_sequence(dst)

            if self.assertEqual(result, seq):
                break

    def test_square_821_patience_callee_save(self):
        src = [MemoryFragment(64, '{}(%rsi)'.format(i*8))for i in range(16)]
        dst = [MemoryFragment(64, '{}(%rdi)'.format(i*8)) for i in range(16)]
        seq = sqGF2N.gen_sequence(5, 821)
        sequence_to_values(src, range(0, 821), padding=ZERO)

        sqGF2N.square_821_patience(dst, src, 5, 5)
        result = sqGF2N.registers_to_sequence(dst)

        self.assertEqual(result, seq)


class TestSquaringModGF2N_permutations(unittest.TestCase):

    def test_square_821_shufbytes(self):
        src = [MemoryFragment(256, '{}(%rsi)'.format(i*32)) for i in range(4)]
        dst = [MemoryFragment(256, '{}(%rdi)'.format(i*32)) for i in range(4)]

        for n in [1, 3, 6, 12, 24, 48, 51, 102, 204, 408]:
            seq = sqGF2N.gen_sequence(n, 821)
            sequence_to_values(src, range(0, 821), padding=ZERO)

            sqGF2N.square_821_shufbytes(dst, src, n)
            result = sqGF2N.registers_to_sequence(dst)

            if self.assertEqual(result, seq):
                break

if __name__ == '__main__':
    unittest.main()
