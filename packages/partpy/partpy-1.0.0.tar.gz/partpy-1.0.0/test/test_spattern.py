import unittest
from partpy.sourcestring import SourceString
from partpy import spattern as pat


class Test_String_Patterns(unittest.TestCase):

    def test_alphas(self):
        MAT = SourceString()
        MAT.set_string('hello world')
        MAT2 = SourceString()
        MAT2.set_string('HEllo world')

        self.assertEqual(MAT.match_string_pattern(pat.alphal), 'hello')
        self.assertEqual(MAT2.match_string_pattern(pat.alphau), 'HE')
        self.assertEqual(MAT.match_string_pattern(pat.alpha), 'hello')

    def test_numbers(self):
        MAT = SourceString()
        MAT.set_string('1234.5')
        MAT2 = SourceString()
        MAT2.set_string('-1234.5')

        self.assertEqual(MAT.match_string_pattern(pat.number), '1234')
        self.assertEqual(MAT2.match_string_pattern(pat.number), '')

    def test_specials(self):
        MAT = SourceString()
        MAT.set_string('hello.world')
        MAT2 = SourceString()
        MAT2.set_string('-1234')

        self.assertEqual(MAT.match_string_pattern(*pat.identifier), 'hello')
        self.assertEqual(MAT.match_string_pattern(*pat.qualified), 'hello.world')
        self.assertEqual(MAT2.match_string_pattern(*pat.integer), '-1234')


if __name__ == "__main__":
    unittest.main()
