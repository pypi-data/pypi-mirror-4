import unittest
from examples.contacts import PARSER, EXPECTED


class Test_Contacts(unittest.TestCase):

    def test_contacs_output(self):
        output = PARSER.parse()
        self.assertEqual(output, EXPECTED)

if __name__ == "__main__":
    unittest.main()
