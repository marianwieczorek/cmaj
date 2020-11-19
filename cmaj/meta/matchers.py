from typing import List

from cmaj.lexical.scanner import Matcher


def matchers() -> List[Matcher]:
    return [comments(), strings(), identifiers(), spaces(), *symbols(), eol()]


def comments() -> Matcher:
    from cmaj.lexical.regex import FirstOf, Repeat, Seq
    from cmaj.lexical.strings import expand
    comment = Seq('#', ' ', Repeat(FirstOf(*expand(' ', '~')), at_least=1))
    return Matcher('comment', comment)


def strings() -> Matcher:
    from cmaj.lexical.regex import FirstOf, Repeat, Seq
    from cmaj.lexical.strings import expand
    single_quoted_string = Seq("'", Repeat(FirstOf(*expand(' ', '~', exclude="'")), at_least=1), "'")
    double_quoted_string = Seq('"', Repeat(FirstOf(*expand(' ', '~', exclude='"')), at_least=1), '"')
    return Matcher('string', FirstOf(single_quoted_string, double_quoted_string))


def identifiers() -> Matcher:
    from cmaj.lexical.regex import FirstOf, Repeat
    from cmaj.lexical.strings import expand
    terminal = Repeat(FirstOf(*expand('a', 'z'), '_'), at_least=1)
    reference = Repeat(FirstOf(*expand('A', 'Z'), '_'), at_least=1)
    return Matcher('identifier', FirstOf(terminal, reference))


def spaces() -> Matcher:
    from cmaj.lexical.regex import Repeat
    return Matcher('space', Repeat(' ', at_least=1))


def symbols() -> List[Matcher]:
    from cmaj.lexical.regex import Eq
    values = ['=', '|', ',']
    return [Matcher(value, Eq(value)) for value in values]


def eol() -> Matcher:
    from cmaj.lexical.regex import Eq
    return Matcher('eol', Eq('\n'))
