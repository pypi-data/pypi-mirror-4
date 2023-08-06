import unittest
from partpy.sourcestring import SourceString


class Test_SourceString(unittest.TestCase):

    def test_has_space(self):
        SRC = SourceString()
        SRC.set_string('hello world')

        self.assertEqual(SRC.has_space(), True)
        self.assertEqual(SRC.has_space(11), True)
        self.assertEqual(SRC.has_space(12), False)
        SRC.eat_length(11)

        self.assertEqual(SRC.has_space(), False)

    def test_eat_string(self):
        SRC = SourceString()
        SRC.set_string('hello world')

        SRC.eat_string('hello world')
        self.assertTrue(SRC.eos)

    def test_eat_string_multiline_peices(self):
        SRC = SourceString()
        SRC.set_string('hello\nworld')

        SRC.eat_string(SRC.get_length(5))
        self.assertEqual(SRC.row, 0)
        self.assertEqual(SRC.col, 5)

        self.assertEqual(SRC.get_char(), '\n')
        SRC.eat_string(SRC.get_char())
        self.assertEqual(SRC.row, 1)
        self.assertEqual(SRC.col, 0)

        SRC.eat_string(SRC.get_length(5))
        self.assertEqual(SRC.row, 1)
        self.assertEqual(SRC.col, 5)
        self.assertEqual(SRC.get_char(), '')

    def test_eat_string_multiline_chunk(self):
        SRC = SourceString()
        SRC.set_string('hello\nworld')

        SRC.eat_string('hello\nworld')
        self.assertEqual(SRC.row, 1)
        self.assertEqual(SRC.col, 5)
        self.assertEqual(SRC.get_char(), '')

    def test_get_length(self):
        SRC = SourceString()
        SRC.set_string('hello world')

        self.assertEqual(SRC.get_length(5), 'hello')
        self.assertEqual(SRC.get_length(11), 'hello world')
        self.assertEqual(SRC.get_length(12), '')
        self.assertEqual(SRC.get_length(12,  True), 'hello world')

    def test_get_char(self):
        SRC = SourceString()
        SRC.set_string('hello world')

        self.assertEqual(SRC.get_char(), 'h')
        SRC.eat_length(10)
        self.assertEqual(SRC.get_char(), 'd')
        SRC.eat_length(1)
        self.assertTrue(SRC.eos)
        self.assertEqual(SRC.get_char(), '')

    def test_get_string(self):
        SRC = SourceString()
        SRC.set_string('hello world')

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
        SRC = SourceString()
        SRC.set_string('hello\nworld\nthis\nis\na\ntest')

        self.assertEqual(SRC.get_line(), 'hello')
        SRC.eat_string('hello\n')
        self.assertEqual(SRC.get_line(), 'world')

    def test_get_lines(self):
        SRC = SourceString()
        SRC.set_string('hello\nworld\nthis\nis\na\ntest')

        lines = SRC.get_lines()
        self.assertEqual(lines, 'hello\nworld')

        SRC.eat_string('hello\nworld\n')
        lines = SRC.get_lines()
        self.assertEqual(lines, 'world\nthis\nis')

        lines = SRC.get_lines(1,0)
        self.assertEqual(lines, 'world\nthis')

        SRC.eat_string('this\nis\na\n')
        lines = SRC.get_lines()
        self.assertEqual(lines, 'a\ntest')


if __name__ == "__main__":
    unittest.main()
