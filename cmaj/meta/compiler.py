from typing import List

from cmaj.ast.node import Node
from cmaj.parser.grammar import Grammar, Rule


def compile_grammar(grammar_node: Node) -> Grammar:
    from cmaj.ast.simplify import squash, prune, skip
    grammar_node = squash(grammar_node, 'GRAMMAR', 'OPTION', 'SEQUENCE')
    grammar_node = prune(grammar_node, 'comment', '=', '|', 'eol')
    grammar_node = skip(grammar_node, 'LINE', 'ANCHOR')

    rules: List[Rule] = []
    for definition_node in grammar_node.children:
        identifier, option = definition_node.children
        rules += compile_rules(identifier.token.value, option)
    return Grammar(*rules)


def compile_rules(rule_key: str, option_node: Node) -> List[Rule]:
    return [Rule(rule_key, compile_symbols(sequence_node)) for sequence_node in option_node.children]


def compile_symbols(sequence_node: Node) -> List[str]:
    return [compile_symbol(anchor_node) for anchor_node in sequence_node.children]


def compile_symbol(anchor_node: Node) -> str:
    assert anchor_node.key in {'identifier', 'string'}
    if anchor_node.key == 'identifier':
        return anchor_node.token.value
    return anchor_node.token.value[1:-1]
