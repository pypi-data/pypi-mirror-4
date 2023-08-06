"""SourceString stores the entire string to be parsed in memory and provides
some simple methods for retrieving and moving current position aswell as methods
for matching strings and patterns.
"""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'


class SourceString(object):
    """Stores the parse string and its length followed by current position
    in the string and if the end of the string has been reached.

    It also stores the current row and column position as manually counted.

    Provides multiple methods for matching strings and patterns and working with
    the source string.
    """
    def __init__(self, string = None):
        self.string = ''
        self.length = 0
        self.pos = 0
        self.col = 0
        self.row = 0
        self.eos = 0
        if string is not None:
            self.set_string(string)

    def load_file(self, filename):
        """Read in file contents and set the current string."""
        with open(filename, 'r') as sourcefile:
            self.set_string(sourcefile.read())

    def set_string(self, string):
        """Set the working string and its length then reset positions."""
        self.string = string
        self.length = len(string)
        self.reset_position()

    def add_string(self, string):
        """Add to the working string and its length and reset eos."""
        self.string += string
        self.length += len(string)
        self.eos = 0

    def reset_position(self):
        """Reset all current positions."""
        self.pos = 0
        self.col = 0
        self.row = 0
        self.eos = 0

    def has_space(self, length = 1):
        """Returns boolean if self.pos + length < working string length."""
        return self.pos + length-1 < self.length

    def eat_length(self, length):
        """Move current position by length and set eos if not has_space()."""

        self.col += length
        self.pos += length

        if not self.has_space():  # Set eos if there is no more space left.
            self.eos = 1

    def eat_string(self, string):
        """Move current position by length of string and count lines by \n."""
        if string == '\n':  # Handle single newline.
            self.col = -1
            self.row += 1
            self.eat_length(1)
        elif '\n' in string:  # Handle string containing a newline.
            for char in string:  # Recursively call eat to handle each char.
                self.eat_string(char)
        else:
            length = len(string)
            self.eat_length(length)  # Any other string just eat the length.

    def get_char(self):
        """Return the current character in the working string."""
        if not self.has_space():
            return ''

        return self.string[self.pos]

    def get_length(self, length, trim = 0):
        """Return string at current position + length.
        If trim == true then get as much as possible before eos"""
        if not self.has_space():
            return ''

        pos = self.pos
        distance = pos + length
        if not trim and not self.has_space(length):
            return ''
        return self.string[pos:distance]

    def get_string(self):
        """Return non space chars from current position until a whitespace."""
        if not self.has_space():
            return ''

        pos = self.pos
        string = self.string
        # Get a char for each char in the current string from pos onward
        #  solong as the char is not whitespace.
        # The following is not yet supported with cython 0.18.0
        #from itertools import takewhile
        #chars = (y for y in takewhile(lambda x: not x.isspace(), string[pos:]))
        chars = []
        for char in string[pos:]:
            if char.isspace():
                break
            else:
                chars.append(char)
        return ''.join(chars)

    def generator(self, offset = 0):
        """A generator for the current position to the end, pure python."""
        for char in self.string[self.pos + offset:]:
            yield char

    def rest_of_string(self, offset = 0):
        """A copy of the current position till the end of the string."""
        return self.string[self.pos + offset:]

    def get_line(self, lineno):
        """Return any line as a SourceLine and None if lineno doesnt exist."""
        line = 0
        output = []
        for char in self.string:
            if line == lineno:
                output.append(char)
            elif line > lineno:
                break

            if char == '\n':
                line += 1
        if not output:
            return None

        return SourceLine(''.join(output), lineno)

    def get_current_line(self):
        """Return a SourceLine of the current line."""
        pos = self.pos - self.col
        string = self.string
        end = self.length

        output = []
        while string[pos] != '\n':
            output.append(string[pos])
            pos += 1
            if pos == end:
                break
        if not output:
            return None

        return SourceLine(''.join(output) + '\n', self.row)

    def get_lines(self, first, last):
        """Return SourceLines for lines between and including first and last."""
        line = 0
        linestring = []
        linestrings = []
        for char in self.string:
            if line >= first and line <= last:
                linestring.append(char)
                if char == '\n':
                    linestrings.append(''.join(linestring))
                    linestring = []
            elif line > last:
                break

            if char == '\n':
                line += 1
        if linestring:
            linestrings.append(''.join(linestring))
        elif not linestrings:
            return None

        return [SourceLine(line, first + num) for num, line in \
            enumerate(linestrings)]

    def get_surrounding_lines(self, past = 1, future = 1):
        """Return the current line and x,y previous and future lines.
        Returns a list of SourceLine's"""
        string = self.string
        pos = self.pos - self.col
        end = self.length
        row = self.row

        linesback = 0
        while linesback > -past:
            if pos <= 0:
                break
            elif string[pos - 2] == '\n':
                linesback -= 1
            pos -= 1

        output = []
        linestring = []
        lines = future + 1
        while linesback < lines:
            if pos >= end:
                linestring.append(string[pos - 1])
                output.append(
                    SourceLine(''.join(linestring[:-1]), row + linesback))
                break
            elif string[pos] == '\n':
                linestring.append(string[pos])
                pos += 1
                output.append(
                    SourceLine(''.join(linestring), row + linesback))
                linesback += 1
                linestring = []
            linestring.append(string[pos])
            pos += 1

        return output

    def match_string(self, string, word = 0):
        """Returns 1 if string can be matches against SourceString's
        current position.

        If word is >= 1 then it will only match string followed by whitepsace"""
        if word:
            return self.get_string() == string
        return self.get_length(len(string)) == string

    def match_any_string(self, strings, word = 0):
        """Attempts to match each string in strings in order of length.
        Will return the string that matches or an empty string if no match.
        Sorts strings list by string length, consider immutability.

        if Word then only match if string is followed by a whitespace."""
        current = ''
        if word:
            current = self.get_string()
            return current if self.get_string() in strings else ''

        strings = sorted(strings, key = len)

        currentlength = 0
        length = 0
        for string in strings:
            length = len(string)
            if length != currentlength:
                current = self.get_length(length)
            if string == current:
                return string
        return ''

    def match_any_char(self, chars):
        """Match and return the current SourceString char if its in chars."""
        current = self.string[self.pos]
        return current if current in chars else ''

    def match_pattern(self, first, rest = None):
        """Match each char sequentially from current SourceString position
        until the pattern doesnt match and return all maches.

        First may be a list or tuple that will get unpacked to first, rest.

        If rest is defined then first is used only to match the first arg
        and the rest of the chars are matched against rest."""
        ftype = type(first)
        if rest is None and ftype in (tuple, list):
            first, rest = first

        firstchar = self.string[self.pos]
        if not firstchar in first:
            return ''

        output = [firstchar]
        pattern = first if rest is None else rest

        for char in self.string[self.pos + 1:]:
            if char in pattern:
                output.append(char)
            else:
                break
        return ''.join(output)

    def match_function(self, first, rest = None):
        """Match each char sequentially from current SourceString position
        until the pattern doesnt match and return all maches.

        First may be a list or tuple that will get unpacked to first, rest.

        This version takes functions instead of string patterns.
        Each function must take one argument, a string, and return a
        value that can be evauluated as True or False.

        If rest is defined then first is used only to match the first arg
        and the rest of the chars are matched against rest."""
        ftype = type(first)
        if rest is None and ftype in (tuple, list):
            first, rest = first

        firstchar = self.string[self.pos]
        if not first(firstchar):
            return ''

        output = [firstchar]
        pattern = first if rest is None else rest

        for char in self.string[self.pos + 1:]:
            if pattern(char):
                output.append(char)
            else:
                break
        return ''.join(output)

    def count_indents(self, spacecount, tabs = 0):
        """Counts the number of indents that can be tabs or spacecount
        number of spaces in a row from the current position."""
        spaces = 0
        indents = 0
        for char in self.string[self.pos - self.col:]:
            if char == ' ':
                spaces += 1
            elif tabs and char == '\t':
                indents += 1
                spaces = 0
            else:
                break
            if spaces == spacecount:
                indents += 1
                spaces = 0
        return indents

    def count_indents_length(self, spacecount, tabs = 0):
        """Counts the number of indents that can be tabs or spacecount
        number of spaces in a row from the current position.

        Also returns the character length of the indents.
        """
        spaces = 0
        indents = 0
        charlen = 0
        for char in self.string[self.pos - self.col:]:
            if char == ' ':
                spaces += 1
            elif tabs and char == '\t':
                indents += 1
                spaces = 0
            else:
                break
            charlen += 1
            if spaces == spacecount:
                indents += 1
                spaces = 0
        return (indents, charlen)

    def __repr__(self):
        return self.string


class SourceLine(SourceString):
    """Contains an entire line of a source with handy line specific methods."""

    def __init__(self, string, lineno):
        super(SourceLine, self).__init__(string)
        self.lineno = lineno

    def strip_trailing_ws(self):
        """Remove trailing whitespace from internal string."""
        self.string = self.string.rstrip()

    def get_first_char(self):
        """Return the first non-whitespace character of the line."""
        for char in self.string:
            if not char.isspace():
                return char

    def get_last_char(self):
        """Return the last non-whitespace character of the line."""
        for char in reversed(self.string):
            if not char.isspace():
                return char

    def __str__(self):
        """Return a string of this line including linenumber."""
        lineno = self.lineno
        padding = 0
        if lineno < 1000:
            padding = 1
        if lineno < 100:
            padding = 2
        if lineno < 10:
            padding = 3

        return str(lineno) + (' ' * padding) + '|' + self.string
