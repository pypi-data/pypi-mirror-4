from partpy.sourcestring import SourceString


class Test_SourceString(object):

    def test_has_space(self):
        SRC = SourceString('hello world')

        assert SRC.has_space() == True
        assert SRC.has_space(11) == True
        assert SRC.has_space(12) == False
        SRC.eat_length(11)

        assert SRC.has_space() == False

    def test_eol_distance_next(self):
        SRC = SourceString('hello world')

        assert SRC.eol_distance_next() == 11
        SRC.eat_string('hello')
        assert SRC.eol_distance_next() == 6

    def test_eol_distance_last(self):
        SRC = SourceString('hello world')

        assert SRC.eol_distance_last() == 0
        SRC.eat_string('hello')
        assert SRC.eol_distance_last() == 5

    def test_spew_length(self):
        SRC = SourceString('hello world')

        SRC.eat_string('hello world')
        assert SRC.eos
        SRC.spew_length(1)
        assert SRC.get_char() == 'd'
        SRC.spew_length(10)
        assert SRC.get_char() == 'h'
        SRC.spew_length(3)
        assert SRC.get_char() == 'h'

    def test_spew_length_multiline_peices(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_length(11)
        assert SRC.row == 2
        assert SRC.col == 5
        assert SRC.get_char() == ''
        assert SRC.eos

        SRC.spew_length(5)
        assert SRC.row == 2
        assert SRC.col == 0
        assert SRC.get_char() == 'w'
        assert not SRC.eos

        SRC.spew_length(6)
        assert SRC.row == 1
        assert SRC.col == 0
        assert SRC.get_char() == 'h'

    def test_eat_string(self):
        SRC = SourceString('hello world')

        SRC.eat_string('hello world')
        assert SRC.eos

    def test_eat_string_multiline_peices(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_string(SRC.get_length(5))
        assert SRC.row == 1
        assert SRC.col == 5

        assert SRC.get_char() == '\n'
        SRC.eat_string(SRC.get_char())
        assert SRC.row == 2
        assert SRC.col == 0

        SRC.eat_string(SRC.get_length(5))
        assert SRC.row == 2
        assert SRC.col == 5
        assert SRC.get_char() == ''

    def test_eat_string_multiline_chunk(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_string('hello\nworld')
        assert SRC.row == 2
        assert SRC.col == 5
        assert SRC.get_char() == ''

    def test_eat_line(self):
        SRC = SourceString('hello\nworld')

        SRC.eat_line()
        assert SRC.row == 2
        assert SRC.col == 0
        assert SRC.get_char() == 'w'

        SRC.eat_line()
        assert SRC.row == 2
        assert SRC.col == 5
        assert SRC.get_char() == ''

    def test_get_length(self):
        SRC = SourceString('hello world')

        assert SRC.get_length(5) == 'hello'
        assert SRC.get_length(11) == 'hello world'
        assert SRC.get_length(12) == ''
        assert SRC.get_length(12, True) == 'hello world'

    def test_get_char(self):
        SRC = SourceString('hello world')

        assert SRC.get_char() == 'h'
        SRC.eat_length(10)
        assert SRC.get_char() == 'd'
        SRC.eat_length(1)
        assert SRC.eos
        assert SRC.get_char() == ''

    def test_get_string(self):
        SRC = SourceString('hello world')

        assert SRC.get_string() == 'hello'
        SRC.eat_length(5)
        assert SRC.get_string() == ''
        SRC.eat_length(1)
        assert SRC.get_string() == 'world'
        SRC.eat_length(5)
        assert SRC.get_string() == ''
        SRC.eat_length(5)
        assert SRC.eos

    def test_get_line(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        assert repr(SRC.get_line(0)) == 'hello\n'
        assert repr(SRC.get_line(2)) == 'this\n'
        assert SRC.get_line(20) == None

    def test_get_current_line(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        assert repr(SRC.get_current_line()) == 'hello\n'
        SRC.eat_string('hello\n')
        assert repr(SRC.get_current_line()) == 'world\n'

    def test_get_lines(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        lines = [str(x) for x in SRC.get_lines(1, 2)]
        assert lines == ['1   |hello\n', '2   |world\n']
        lines = ''.join([repr(x) for x in SRC.get_lines(0, 2)])
        assert lines == 'hello\nworld\n'

        lines = [str(x) for x in SRC.get_lines(5, 6)]
        assert lines == ['5   |a\n', '6   |test']
        lines = ''.join([repr(x) for x in SRC.get_lines(5, 6)])
        assert lines == 'a\ntest'

        assert SRC.get_lines(10, 20) == None

    def test_get_all_lines(self):
        base = 'hello\nworld\nthis\nis\na\ntest'
        SRC = SourceString(base)

        lines = [str(x) for x in SRC.get_all_lines()]
        expected = ['1   |hello\n', '2   |world\n', '3   |this\n', '4   |is\n',
            '5   |a\n', '6   |test']
        assert lines == expected
        lines = ''.join([repr(x) for x in SRC.get_all_lines()])
        assert lines == base

    def test_get_surrounding_lines(self):
        SRC = SourceString('hello\nworld\nthis\nis\na\ntest')

        lines = [str(x) for x in SRC.get_surrounding_lines()]
        assert lines == ['1   |hello\n', '2   |world\n']
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        assert lines == 'hello\nworld\n'

        SRC.eat_string('hello\nworld\n')

        lines = [str(x) for x in SRC.get_surrounding_lines()]
        assert lines == ['2   |world\n', '3   |this\n', '4   |is\n']
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        assert lines == 'world\nthis\nis\n'

        lines = [str(x) for x in SRC.get_surrounding_lines(1, 0)]
        assert lines == ['2   |world\n', '3   |this\n']
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines(1, 0)])
        assert lines == 'world\nthis\n'

        SRC.eat_string('this\nis\na\n')
        lines = [str(x) for x in SRC.get_surrounding_lines()]
        assert lines == ['5   |a\n', '6   |test']
        lines = ''.join([repr(x) for x in SRC.get_surrounding_lines()])
        assert lines == 'a\ntest'

    def test_match_string(self):
        MAT = SourceString('hello world\ntesting stuff')

        assert MAT.match_string('hello', 1) == True
        assert MAT.match_string('hello') == True
        assert MAT.match_string('hel', 1) == False
        assert MAT.match_string('hel') == True
        assert MAT.match_string('hello world', 1) == False
        assert MAT.match_string('hello world') == True

    def test_match_any_string(self):
        MAT = SourceString('import partpy')
        strings = ['def', 'imp', 'import ', 'import']

        assert MAT.match_any_string(strings) == 'imp'
        assert MAT.match_any_string(strings, 1) == 'import'

    def test_match_any_char(self):
        MAT = SourceString('import partpy')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        assert MAT.match_any_char(alphas) == 'i'
        assert MAT.match_any_char(alphas.replace('i', '')) == ''

    def test_match_string_pattern(self):
        MAT = SourceString('Nekroze')
        alphas = 'abcdefghijklmnopqrstuvwxyz'

        assert MAT.match_string_pattern(alphas.upper()) == 'N'
        assert MAT.match_string_pattern(alphas.upper(), alphas) == 'Nekroze'
        assert MAT.match_string_pattern(alphas) == ''

    def test_match_function_pattern(self):
        MAT = SourceString('Test100')

        assert MAT.match_function_pattern(str.isalpha) == 'Test'
        assert MAT.match_function_pattern(str.isalpha, str.isalnum) == 'Test100'
        assert MAT.match_function_pattern(str.isdigit) == ''

        assert MAT.match_function_pattern(lambda c: c == 'T' or c in 'te') == 'Te'
        lam = (lambda c: c == 'T', lambda c: c == 'e')
        assert MAT.match_function_pattern(*lam) == 'Te'

    def test_count_indents(self):
        MAT = SourceString('  \tTest100')

        assert MAT.count_indents(2, 1) == 2
        assert MAT.count_indents(2) == 1

    def test_count_indents_length(self):
        MAT = SourceString('  \tTest100')

        assert MAT.count_indents_length(2, 1) == (2, 3)
        assert MAT.count_indents_length(2) == (1, 2)

    def test_count_indents_last_line(self):
        MAT = SourceString('Test100\n  test\n  more')

        assert MAT.count_indents_last_line(2) == 0
        MAT.eat_length(8)
        assert MAT.count_indents_last_line(2) == 0
        MAT.eat_length(7)
        assert MAT.count_indents_last_line(2) == 1

    def test_count_indents_length_last_line(self):
        MAT = SourceString('Test100\n  test\n  more')

        assert MAT.count_indents_length_last_line(2) == (0, 0)
        MAT.eat_length(8)
        assert MAT.count_indents_length_last_line(2) == (0, 0)
        MAT.eat_length(7)
        assert MAT.count_indents_length_last_line(2) == (1, 2)

    def test_skip_whitespace(self):
        MAT = SourceString('  \tTest100')
        MAT2 = SourceString('  \nTest100')

        MAT.skip_whitespace()
        assert MAT.get_char() == 'T'

        MAT2.skip_whitespace()
        assert MAT2.get_char() == '\n'
        MAT2.skip_whitespace(1)
        assert MAT2.get_char() == 'T'

    def test_iterator(self):
        string = 'nekroze'
        MAT = SourceString(string)

        assert string == ''.join(MAT)
        #for i, char in enumerate(MAT):
        #    assert string[i] == char
