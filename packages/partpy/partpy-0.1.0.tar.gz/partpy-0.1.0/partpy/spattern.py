"""Predefined string patterns for use in Matcher.match_string methods."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'

alphal = 'abcdefghijklmnopqrstuvwxyz'
alphau = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alpha = alphal + alphau

number = '0123456789'
alnum = alpha + number

identifier = (alpha, alnum + '_')
qualified = (alpha, alpha + '.')
integer = (number + '-', number)
