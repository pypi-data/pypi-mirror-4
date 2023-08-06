import unittest
from partpy.matcher import Matcher


class Test_Matcher(unittest.TestCase):

    def test_match_string(self):
        MAT = Matcher()
        MAT.set_string('hello world\ntesting stuff')

        self.assertEqual(MAT.match_string('hello', 1), True)
        self.assertEqual(MAT.match_string('hello'), True)
        self.assertEqual(MAT.match_string('hel', 1), False)
        self.assertEqual(MAT.match_string('hel'), True)
        self.assertEqual(MAT.match_string('hello world', 1), False)
        self.assertEqual(MAT.match_string('hello world'), True)

    def test_match_any_string(self):
        MAT = Matcher()
        MAT.set_string('import partpy')
        strings = ['import ', 'def', 'import', 'imp']

        self.assertEqual(MAT.match_any_string(strings), 'imp')
        self.assertEqual(MAT.match_any_string(strings, 1), 'import')

    def test_match_any_char(self):
        MAT = Matcher()
        MAT.set_string('import partpy')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        self.assertEqual(MAT.match_any_char(alphas), 'i')
        self.assertEqual(MAT.match_any_char(alphas.replace('i', '')), '')

    def test_match_pattern(self):
        MAT = Matcher()
        MAT.set_string('Nekroze')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        self.assertEqual(MAT.match_pattern(alphas.upper()), 'N')
        self.assertEqual(MAT.match_pattern([alphas.upper(), alphas]), 'Nekroze')
        self.assertEqual(MAT.match_pattern(alphas), '')

    def test_match_function(self):
        MAT = Matcher()
        MAT.set_string('Test100')

        self.assertEqual(MAT.match_function(str.isalpha), 'Test')
        self.assertEqual(MAT.match_function(str.isalpha, str.isalnum), 'Test100')
        self.assertEqual(MAT.match_function(str.isdigit), '')

        self.assertEqual(MAT.match_function(lambda c: c == 'T' or c in 'te'), 'Te')
        lam = (lambda c: c == 'T', lambda c: c == 'e')
        self.assertEqual(MAT.match_function(lam), 'Te')

    def test_count_indents(self):
        MAT = Matcher()
        MAT.set_string('  \tTest100')

        self.assertEqual(MAT.count_indents(2, 1), 2)
        self.assertEqual(MAT.count_indents(2), 1)

    def test_count_indents_length(self):
        MAT = Matcher()
        MAT.set_string('  \tTest100')

        self.assertEqual(MAT.count_indents_length(2, 1), (2, 3))
        self.assertEqual(MAT.count_indents_length(2), (1, 2))


if __name__ == "__main__":
    unittest.main()
