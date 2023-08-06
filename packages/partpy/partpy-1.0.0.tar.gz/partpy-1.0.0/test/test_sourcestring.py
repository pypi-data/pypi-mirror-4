import unittest
from partpy.sourcestring import SourceString


class Test_SourceString(unittest.TestCase):

    def test_has_space(self):
        SRC = SourceString('hello world')

        self.assertEqual(SRC.has_space(), True)
        self.assertEqual(SRC.has_space(11), True)
        self.assertEqual(SRC.has_space(12), False)
        SRC.eat_length(11)

        self.assertEqual(SRC.has_space(), False)

    def test_eat_string(self):
        SRC = SourceString('hello world')

        SRC.eat_string('hello world')
        self.assertTrue(SRC.eos)

    def test_eat_string_multiline_peices(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_string(SRC.get_length(5))
        self.assertEqual(SRC.row, 1)
        self.assertEqual(SRC.col, 5)

        self.assertEqual(SRC.get_char(), '\n')
        SRC.eat_string(SRC.get_char())
        self.assertEqual(SRC.row, 2)
        self.assertEqual(SRC.col, 0)

        SRC.eat_string(SRC.get_length(5))
        self.assertEqual(SRC.row, 2)
        self.assertEqual(SRC.col, 5)
        self.assertEqual(SRC.get_char(), '')

    def test_eat_string_multiline_chunk(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_string('hello\nworld')
        self.assertEqual(SRC.row, 2)
        self.assertEqual(SRC.col, 5)
        self.assertEqual(SRC.get_char(), '')

    def test_eat_line(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_line()
        self.assertEqual(SRC.row, 2)
        self.assertEqual(SRC.col, 0)
        self.assertEqual(SRC.get_char(), 'w')

        SRC.eat_line()
        self.assertEqual(SRC.row, 2)
        self.assertEqual(SRC.col, 5)
        self.assertEqual(SRC.get_char(), '')

    def test_get_length(self):
        SRC = SourceString('hello world')

        self.assertEqual(SRC.get_length(5), 'hello')
        self.assertEqual(SRC.get_length(11), 'hello world')
        self.assertEqual(SRC.get_length(12), '')
        self.assertEqual(SRC.get_length(12,  True), 'hello world')

    def test_get_char(self):
        SRC = SourceString('hello world')

        self.assertEqual(SRC.get_char(), 'h')
        SRC.eat_length(10)
        self.assertEqual(SRC.get_char(), 'd')
        SRC.eat_length(1)
        self.assertTrue(SRC.eos)
        self.assertEqual(SRC.get_char(), '')

    def test_get_string(self):
        SRC = SourceString('hello world')

        self.assertEqual(SRC.get_string(), 'hello')
        SRC.eat_length(5)
        self.assertEqual(SRC.get_string(), '')
        SRC.eat_length(1)
        self.assertEqual(SRC.get_string(), 'world')
        SRC.eat_length(5)
        self.assertEqual(SRC.get_string(), '')
        SRC.eat_length(5)
        self.assertTrue(SRC.eos)

    def test_get_line(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        self.assertEqual(repr(SRC.get_line(0)), 'hello\n')
        self.assertEqual(repr(SRC.get_line(2)), 'this\n')
        self.assertEqual(SRC.get_line(20), None)

    def test_get_current_line(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        self.assertEqual(repr(SRC.get_current_line()), 'hello\n')
        SRC.eat_string('hello\n')
        self.assertEqual(repr(SRC.get_current_line()), 'world\n')

    def test_get_lines(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        lines = [str(x) for x in SRC.get_lines(1, 2)]
        self.assertEqual(lines, ['1   |hello\n', '2   |world\n'])
        lines = ''.join([repr(x) for x in SRC.get_lines(0, 2)])
        self.assertEqual(lines, 'hello\nworld\n')

        lines = [str(x) for x in SRC.get_lines(5, 6)]
        self.assertEqual(lines, ['5   |a\n', '6   |test'])
        lines = ''.join([repr(x) for x in SRC.get_lines(5, 6)])
        self.assertEqual(lines, 'a\ntest')

        self.assertEqual(SRC.get_lines(10, 20), None)

    def test_get_all_lines(self):
        base = 'hello\nworld\nthis\nis\na\ntest'
        SRC = SourceString(base)

        lines = [str(x) for x in SRC.get_all_lines()]
        expected = ['1   |hello\n', '2   |world\n', '3   |this\n', '4   |is\n',
            '5   |a\n', '6   |test']
        self.assertEqual(lines, expected)
        lines = ''.join([repr(x) for x in SRC.get_all_lines()])
        self.assertEqual(lines, base)

    def test_get_surrounding_lines(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        lines = [str(x) for x in SRC.get_surrounding_lines()]
        self.assertEqual(lines, ['1   |hello\n', '2   |world\n'])
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        self.assertEqual(lines, 'hello\nworld\n')

        SRC.eat_string('hello\nworld\n')

        lines = [str(x) for x in SRC.get_surrounding_lines()]
        self.assertEqual(lines, ['2   |world\n', '3   |this\n', '4   |is\n'])
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        self.assertEqual(lines, 'world\nthis\nis\n')

        lines = [str(x) for x in SRC.get_surrounding_lines(1, 0)]
        self.assertEqual(lines, ['2   |world\n', '3   |this\n'])
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines(1, 0)])
        self.assertEqual(lines, 'world\nthis\n')

        SRC.eat_string('this\nis\na\n')
        lines = [str(x) for x in SRC.get_surrounding_lines()]
        self.assertEqual(lines, ['5   |a\n', '6   |test'])
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        self.assertEqual(lines, 'a\ntest')

    def test_match_string(self):
        MAT = SourceString('hello world\ntesting stuff')

        self.assertEqual(MAT.match_string('hello', 1), True)
        self.assertEqual(MAT.match_string('hello'), True)
        self.assertEqual(MAT.match_string('hel', 1), False)
        self.assertEqual(MAT.match_string('hel'), True)
        self.assertEqual(MAT.match_string('hello world', 1), False)
        self.assertEqual(MAT.match_string('hello world'), True)

    def test_match_any_string(self):
        MAT = SourceString('import partpy')
        strings = ['def', 'imp', 'import ', 'import']

        self.assertEqual(MAT.match_any_string(strings), 'imp')
        self.assertEqual(MAT.match_any_string(strings, 1), 'import')

    def test_match_any_char(self):
        MAT = SourceString('import partpy')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        self.assertEqual(MAT.match_any_char(alphas), 'i')
        self.assertEqual(MAT.match_any_char(alphas.replace('i', '')), '')

    def test_match_string_pattern(self):
        MAT = SourceString('Nekroze')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        self.assertEqual(MAT.match_string_pattern(alphas.upper()), 'N')
        self.assertEqual(MAT.match_string_pattern(alphas.upper(), alphas), 'Nekroze')
        self.assertEqual(MAT.match_string_pattern(alphas), '')

    def test_match_function_pattern(self):
        MAT = SourceString('Test100')

        self.assertEqual(MAT.match_function_pattern(str.isalpha), 'Test')
        self.assertEqual(MAT.match_function_pattern(str.isalpha, str.isalnum), 'Test100')
        self.assertEqual(MAT.match_function_pattern(str.isdigit), '')

        self.assertEqual(MAT.match_function_pattern(lambda c: c == 'T' or c in 'te'), 'Te')
        lam = (lambda c: c == 'T', lambda c: c == 'e')
        self.assertEqual(MAT.match_function_pattern(*lam), 'Te')

    def test_count_indents(self):
        MAT = SourceString('  \tTest100')

        self.assertEqual(MAT.count_indents(2, 1), 2)
        self.assertEqual(MAT.count_indents(2), 1)

    def test_count_indents_length(self):
        MAT = SourceString('  \tTest100')

        self.assertEqual(MAT.count_indents_length(2, 1), (2, 3))
        self.assertEqual(MAT.count_indents_length(2), (1, 2))

    def test_count_indents_last_line(self):
        MAT = SourceString('Test100\n  test\n  more')

        self.assertEqual(MAT.count_indents_last_line(2), 0)
        MAT.eat_length(8)
        self.assertEqual(MAT.count_indents_last_line(2), 0)
        MAT.eat_length(7)
        self.assertEqual(MAT.count_indents_last_line(2), 1)

    def test_count_indents_length_last_line(self):
        MAT = SourceString('Test100\n  test\n  more')

        self.assertEqual(MAT.count_indents_length_last_line(2), (0, 0))
        MAT.eat_length(8)
        self.assertEqual(MAT.count_indents_length_last_line(2), (0, 0))
        MAT.eat_length(7)
        self.assertEqual(MAT.count_indents_length_last_line(2), (1, 2))

    def test_skip_whitespace(self):
        MAT = SourceString('  \tTest100')
        MAT2 = SourceString('  \nTest100')

        MAT.skip_whitespace()
        self.assertEqual(MAT.get_char(), 'T')

        MAT2.skip_whitespace()
        self.assertEqual(MAT2.get_char(), '\n')
        MAT2.skip_whitespace(1)
        self.assertEqual(MAT2.get_char(), 'T')

    def test_iterator(self):
        string = 'nekroze'
        MAT = SourceString(string)

        for i, char in enumerate(MAT):
            self.assertEqual(string[i], char)


if __name__ == "__main__":
    unittest.main()
