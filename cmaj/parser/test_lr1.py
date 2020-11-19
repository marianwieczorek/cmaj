from typing import Any, List, Tuple
from unittest import TestCase

from cmaj.ast.node import Node, Token
from cmaj.parser.grammar import Grammar, Rule, augment
from cmaj.parser.graph import graph_for
from cmaj.parser.lr1 import ParserError, parse
from cmaj.parser.table import table_for


class ParseTest(TestCase):
    def test_given_grammar_with_terminal_and_valid_token_then_ast(self) -> None:
        grammar = augment(Grammar(Rule('A', ['a'])), 'A')
        graph = graph_for(grammar)
        table = table_for(grammar, graph)
        actual_root = parse(tokens('a'), grammar, table)
        self._assert_correct_tree(('A', ('a',)), actual_root)
        self.assertRaises(ParserError, parse, tokens('aa'), grammar, table)

    def test_given_count_grammar_when_00001111_then_ast(self) -> None:
        grammar = augment(Grammar(Rule('X', ['0', 'X', '1']), Rule('X', ['0', '1'])), 'X')
        graph = graph_for(grammar)
        table = table_for(grammar, graph)
        actual_root = parse(tokens('00001111'), grammar, table)
        expected_tree = ('X', '0', ('X', '0', ('X', '0', ('X', '0', '1'), '1'), '1'), '1')
        self._assert_correct_tree(expected_tree, actual_root)
        self.assertRaises(ParserError, parse, tokens('001'), grammar, table)

    def test_given_arithmetic_grammar_when_1add1add1mul1add1_then_ast(self) -> None:
        grammar = augment(Grammar(Rule('ADD', ['ADD', '+', 'MUL']), Rule('ADD', ['MUL']),
                                  Rule('MUL', ['MUL', '*', '1']), Rule('MUL', ['1'])), 'ADD')
        graph = graph_for(grammar)
        table = table_for(grammar, graph)
        actual_root = parse(tokens('1+1+1*1+1'), grammar, table)
        mul_one = ('MUL', '1')
        add_one = ('ADD', mul_one)
        expected_tree = ('ADD', ('ADD', ('ADD', add_one, '+', mul_one), '+', ('MUL', mul_one, '*', '1')), '+', mul_one)
        self._assert_correct_tree(expected_tree, actual_root)
        self.assertRaises(ParserError, parse, tokens('11+1'), grammar, table)

    def _assert_correct_tree(self, expected_nodes: Tuple[Any, ...], actual_root: Node) -> None:
        expected_root_key, expected_children = expected_nodes[0], expected_nodes[1:]
        self.assertEqual(expected_root_key, actual_root.key)
        self.assertEqual(len(expected_children), len(actual_root.children))
        for expected_child, actual_child in zip(expected_children, actual_root.children):
            self._assert_correct_tree(expected_child, actual_child)


def tokens(keys: str) -> List[Node]:
    return [Node(key, token=Token(0, column, 'x')) for column, key in enumerate(keys)]
