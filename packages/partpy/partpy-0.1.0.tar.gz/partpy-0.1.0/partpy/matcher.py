"""Matcher utilizes SourceString to provide some simple string matching
functionality."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'

from .sourcestring import SourceString


class Matcher(SourceString):
    """Subclass of SourceString and methods to assist
    with pattern/string matching against the SoruceString."""

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
        number of spaces in a row."""
        spaces = 0
        indents = 0
        for char in self.string[self.pos:]:
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
        number of spaces in a row.

        Also returns the character length of the indents.
        """
        spaces = 0
        indents = 0
        charlen = 0
        for char in self.string[self.pos:]:
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
