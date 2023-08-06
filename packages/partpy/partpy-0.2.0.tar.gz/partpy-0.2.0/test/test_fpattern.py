import unittest
from partpy.sourcestring import SourceString
from partpy import fpattern as pat


class Test_Function_Patterns(unittest.TestCase):

    def test_alphas(self):
        MAT = SourceString('hello world')
        MAT2 = SourceString('HEllo world')

        self.assertEqual(MAT.match_function(pat.alphal), 'hello')
        self.assertEqual(MAT2.match_function(pat.alphau), 'HE')
        self.assertEqual(MAT.match_function(pat.alpha), 'hello')

    def test_numbers(self):
        MAT = SourceString('1234.5')
        MAT2 = SourceString('-1234.5')

        self.assertEqual(MAT.match_function(pat.number), '1234')
        self.assertEqual(MAT2.match_function(pat.number), '')

    def test_specials(self):
        MAT = SourceString('hello.world')
        MAT2 = SourceString('-1234')

        self.assertEqual(MAT.match_function(pat.identifier), 'hello')
        self.assertEqual(MAT.match_function(pat.qualified), 'hello.world')
        self.assertEqual(MAT2.match_function(pat.integer), '-1234')


if __name__ == "__main__":
    unittest.main()
