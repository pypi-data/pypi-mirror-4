from partpy.sourcestring import SourceString
from partpy import fpattern as pat


class Test_Function_Patterns(object):

    def test_alphas(self):
        MAT = SourceString('hello world')
        MAT2 = SourceString('HEllo world')

        assert MAT.match_function_pattern(pat.alphal) == 'hello'
        assert MAT2.match_function_pattern(pat.alphau) == 'HE'
        assert MAT.match_function_pattern(pat.alpha) == 'hello'

    def test_numbers(self):
        MAT = SourceString('1234.5')
        MAT2 = SourceString('-1234.5')

        assert MAT.match_function_pattern(pat.number) == '1234'
        assert MAT2.match_function_pattern(pat.number) == ''

    def test_specials(self):
        MAT = SourceString('hello.world')
        MAT2 = SourceString('-1234')

        assert MAT.match_function_pattern(*pat.identifier) == 'hello'
        assert MAT.match_function_pattern(*pat.qualified) == 'hello.world'
        assert MAT2.match_function_pattern(*pat.integer) == '-1234'
