"""SourceString utilizes SourceString to provide some simple string matching
functionality."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'

from partpy import SourceString
from partpy import PartpyError
from partpy import spattern as spat

EXAMPLE = '''
Taylor Nekroze Lawson - nekroze@eturnilnetwork.com
Some Random:randomkid@randomail.net
'''
EXPECTED = {'Taylor Nekroze Lawson': 'nekroze@eturnilnetwork.com',
                  'Some Random': 'randomkid@randomail.net'}

class ContactsParser(SourceString):
    """The contacts parser will simply look for name and website pairs
    while disregarding any kind of whitespace and store them in a dict.
    """
    error = False

    def parse(self):
        """Run the parser over the entire sourestring and return the results."""
        try:
            return self.parse_top_level()
        except PartpyError as ex:
            self.error = True
            print(ex.pretty_print())

    def parse_top_level(self):
        """The top level parser will do a loop where it looks for a single
        contact parse and then eats all whitespace until there is no more
        input left or another contact is found to be parsed and stores them.
        """
        contacts = []
        while not self.eos:
            contact = self.parse_contact()  # match a contact expression.
            if not contact:  # There was no contact so end file.
                break  # This would be a nice place to put other expressions.
            contacts.append(contact)
            # skip all whitespace between the end of the last contact and the
            # next non whitespace character, ie until something interesting.
            self.parse_whitespace()
        output = {}
        for key, value in contacts:
            output[key] = value
        return output

    def parse_contact(self):
        """Parse a top level contact expression, these consist of a name
        expression a special char and an email expression.

        The characters found in a name and email expression are returned.
        """
        self.parse_whitespace()
        name = self.parse_name()  # parse a name expression and get the string.
        if not name:  # No name was found so shout it out.
            raise PartpyError(self, 'Expecting a name')

        self.parse_whitespace()
        # allow name and email to be delimited by either a ':' or '-'
        if not self.match_any_char(':-'):
            raise PartpyError(self, 'Expecting : or -')
        self.eat_length(1)
        self.parse_whitespace()

        email = self.parse_email()  # parse an email and store its string.
        if not email:
            raise PartpyError(self, 'Expecting an email address')
        return (name, email)  # return the strings matching a name and email.

    def parse_whitespace(self):
        """This function simply eats chars until the current char is no longer
        a space, tab, newline.
        """
        while True:
            char = self.get_char()  # get the current SourceString character.
            if not char in ['\n', '\t', ' ']:
                break
            else:
                self.eat_length(1)  # eat the whitespace char.

    def parse_name(self):
        """This function uses string patterns to match a title cased name.
        This is done in a loop until there are no more names to match so as
        to be able to include surnames etc. in the output."""
        name = []
        while True:
            # Match the current char until it doesnt match the given pattern:
            # first char must be an uppercase alpha and the rest must be lower
            # cased alphas.
            part = self.match_string_pattern(spat.alphau, spat.alphal)
            if part == '':
                break  # There is no more matchable strings.
            self.eat_string(part)  # Eat the found string
            name.append(part)  # Store this name part
            if self.get_char() == ' ':  # if the current char is a single space
                # eat it. This allows one space between parts
                self.eat_length(1)

        if not len(name):  # if no name parts where detected raise an expection.
            raise PartpyError(self, 'Expecting a title cased name')
        return ' '.join(name)  # return the strings of the names found

    def parse_email(self):
        """Email address parsing is done in several stages.
        First the name of the email use is determined.
        Then it looks for a '@' as a delimiter between the name and the site.
        Lastly the email site is matched.

        Each part's string is stored, combined and returned.
        """
        email = []
        # Match from current char until a non lower cased alpha
        name = self.match_string_pattern(spat.alphal)
        if not name:
            raise PartpyError(self, 'Expected a valid name')

        email.append(name)  # Store the name
        self.eat_string(name)  # Eat the name

        nextchar = self.get_char()
        if not nextchar == '@':
            raise PartpyError(self, 'Expecting @, found: ' + nextchar)

        email.append(nextchar)
        self.eat_length(1)  # Eat the '@' symbol

        # Use string pattern matching to match all lower cased alphas or '.'s.
        site = self.match_string_pattern(spat.alphal + '.')
        if not site:
            raise PartpyError(self, 'Expecting a site, found: ' + site)

        email.append(site)
        self.eat_string(site)  # Eat the site
        return ''.join(email)  # Return the matched string

PARSER = ContactsParser()
PARSER.set_string(EXAMPLE)

def main(argv):  # pylint: disable=W0613
    output = PARSER.parse()
    if PARSER.error or output is None:
        return 1

    for name, email in output.items():
        print(name, ' : ', email)

    return 0  # pylint: enable=W0613

def target(*args):  # pylint: disable=W0613
    return main, None  # pylint: enable=W0613

if __name__ == "__main__":
    import sys
    main(sys.argv)
