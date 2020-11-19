from typing import List

from cmaj.ast.node import Node
from cmaj.parser.grammar import Grammar
from cmaj.parser.table import ParseTable


def meta_grammar() -> Grammar:
    from cmaj.parser.grammar import Rule, augment
    grammar = Grammar(Rule('GRAMMAR', ['LINE', 'GRAMMAR']), Rule('GRAMMAR', ['LINE']),
                      Rule('LINE', ['DEFINITION', 'eol']), Rule('LINE', ['comment', 'eol']), Rule('LINE', ['eol']),
                      Rule('DEFINITION', ['identifier', '=', 'OPTION']),
                      Rule('OPTION', ['SEQUENCE', '|', 'OPTION']), Rule('OPTION', ['SEQUENCE']),
                      Rule('SEQUENCE', ['ANCHOR', 'SEQUENCE']), Rule('SEQUENCE', ['ANCHOR']),
                      Rule('ANCHOR', ['string']), Rule('ANCHOR', ['identifier']))
    return augment(grammar, 'GRAMMAR')


def meta_table() -> ParseTable:
    from cmaj.parser.graph import graph_for
    from cmaj.parser.table import table_for
    grammar = meta_grammar()
    graph = graph_for(grammar)
    return table_for(grammar, graph)


def parse(lines: List[str], grammar: Grammar, table: ParseTable) -> Node:
    from cmaj.lexical.scanner import scan
    from cmaj.meta.matchers import matchers
    from cmaj.parser.lr1 import parse
    tokens = [token for token in scan(lines, matchers()) if token.key != 'space']
    return parse(tokens, grammar, table)
