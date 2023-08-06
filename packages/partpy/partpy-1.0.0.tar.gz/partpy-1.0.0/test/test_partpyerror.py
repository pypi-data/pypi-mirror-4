import unittest
from partpy.sourcestring import SourceString
from partpy.partpyerror import PartpyError


class Test(unittest.TestCase):

    def test_pretty_output(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        expected = '\n1   |hello\n\n     ^\nError[101]'
        string = repr(PartpyError(SRC, 'Error[101]'))
        self.assertEqual(string, expected)


if __name__ == "__main__":
    unittest.main()
