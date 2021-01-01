from typing import List

from cmaj.lexical.scanner import Matcher


def identifiers() -> Matcher:
    from cmaj.lexical.regex import FirstOf, Maybe, Repeat, Seq
    from cmaj.lexical.strings import expand
    alpha = expand('a', 'z')
    digits = expand('0', '9')

    identifier_head = FirstOf(*alpha)
    identifier_body = FirstOf(*alpha, *digits, '_')
    identifier_tail = FirstOf(*alpha, *digits)
    regex = Seq(identifier_head, Repeat(identifier_body), Maybe(identifier_tail))
    return Matcher('identifier', regex)


def types() -> Matcher:
    from cmaj.lexical.regex import FirstOf, Repeat, Seq
    from cmaj.lexical.strings import expand
    alpha_upper = expand('A', 'Z')
    alpha_lower = expand('a', 'z')
    digits = expand('0', '9')

    type_head = FirstOf(*alpha_upper)
    type_body = FirstOf(*alpha_upper, *alpha_lower, *digits)
    regex = Seq(type_head, Repeat(type_body))
    return Matcher('type', regex)


def comments() -> Matcher:
    from cmaj.lexical.regex import Repeat, Seq
    from cmaj.lexical.strings import expand
    visible = expand(' ', '~')
    regex = Seq('#', Repeat(*visible))
    return Matcher('comment', regex)


def keywords() -> List[Matcher]:
    from cmaj.lexical.regex import Eq
    values = ['return']
    return [Matcher(value, Eq(value)) for value in values]


def symbols() -> List[Matcher]:
    from cmaj.lexical.regex import Eq
    values = ['not', 'or', 'and', 'xor'] + \
             ['[', ']'] + \
             ['(', ',', ')', '->'] + \
             ['<', '<=', '==', '!=', '=>', '>'] + \
             ['+', '-', '*', '//', '/', 'mod']
    return [Matcher(value, Eq(value)) for value in values]
