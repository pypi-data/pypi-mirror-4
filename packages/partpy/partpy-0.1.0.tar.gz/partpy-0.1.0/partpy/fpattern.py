"""Predefined function patterns for use in Matcher.match_function methods."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'

alphal = str.islower
alphau = str.isupper
alpha = str.isalpha

number = str.isdigit
alnum = str.isalnum

def _identifier_first(char):
    return alpha(char) or char == '_'

identifier = (_identifier_first, alnum)

def _qualified_rest(char):
    return alpha(char) or char == '.'

qualified = (_identifier_first, _qualified_rest)

def _integer_first(char):
    return number(char) or char == '-'

integer = (_integer_first, number)
