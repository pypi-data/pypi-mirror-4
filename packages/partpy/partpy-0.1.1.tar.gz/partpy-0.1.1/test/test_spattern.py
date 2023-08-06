import unittest
from partpy.matcher import Matcher
from partpy import spattern as pat


class Test_String_Patterns(unittest.TestCase):
    
    def test_alphas(self):
        MAT = Matcher()
        MAT.set_string('hello world')
        MAT2 = Matcher()
        MAT2.set_string('HEllo world')
        
        self.assertEqual(MAT.match_pattern(pat.alphal), 'hello')
        self.assertEqual(MAT2.match_pattern(pat.alphau), 'HE')
        self.assertEqual(MAT.match_pattern(pat.alpha), 'hello')
        
    def test_numbers(self):
        MAT = Matcher()
        MAT.set_string('1234.5')
        MAT2 = Matcher()
        MAT2.set_string('-1234.5')
        
        self.assertEqual(MAT.match_pattern(pat.number), '1234')
        self.assertEqual(MAT2.match_pattern(pat.number), '')
        
    def test_specials(self):
        MAT = Matcher()
        MAT.set_string('hello.world')
        MAT2 = Matcher()
        MAT2.set_string('-1234')
        
        self.assertEqual(MAT.match_pattern(pat.identifier), 'hello')
        self.assertEqual(MAT.match_pattern(pat.qualified), 'hello.world')
        self.assertEqual(MAT2.match_pattern(pat.integer), '-1234')
        

if __name__ == "__main__":
    unittest.main()
