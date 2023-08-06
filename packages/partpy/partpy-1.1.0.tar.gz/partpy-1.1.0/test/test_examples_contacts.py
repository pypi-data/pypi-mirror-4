from examples.contacts import PARSER, EXPECTED

class Test_Contacts(object):

    def test_contacs_output(self):
        output = PARSER.parse()
        assert output == EXPECTED
