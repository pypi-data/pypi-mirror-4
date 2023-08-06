import unittest
from partpy.sourcestring import SourceLine


class Test_SourceLine(unittest.TestCase):

    def test_strip_trailing_ws(self):
        SRC = SourceLine('test \n', 0)
        self.assertEqual(repr(SRC), 'test \n')
        SRC.strip_trailing_ws()
        self.assertEqual(repr(SRC), 'test')

    def test_get_first_char(self):
        SRC = SourceLine('    test\n', 0)
        self.assertEqual(SRC.get_first_char(), 't')

    def test_get_last_char(self):
        SRC = SourceLine('    test\n', 0)
        self.assertEqual(SRC.get_last_char(), 't')


if __name__ == "__main__":
    unittest.main()
