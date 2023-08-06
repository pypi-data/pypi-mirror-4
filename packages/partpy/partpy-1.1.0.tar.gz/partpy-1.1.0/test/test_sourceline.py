from partpy.sourcestring import SourceLine


class Test_SourceLine(object):

    def test_strip_trailing_ws(self):
        SRC = SourceLine('test \n', 0)
        assert repr(SRC) == 'test \n'
        SRC.strip_trailing_ws()
        assert repr(SRC) == 'test'

    def test_get_first_char(self):
        SRC = SourceLine('    test\n', 0)
        assert SRC.get_first_char() == 't'

    def test_get_last_char(self):
        SRC = SourceLine('    test\n', 0)
        assert SRC.get_last_char() == 't'
