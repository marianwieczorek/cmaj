from typing import List, Tuple
from unittest import TestCase

from cmaj.parser.closure import Closure
from cmaj.parser.grammar import Grammar, Rule
from cmaj.parser.graph import graph_for


class ClosureGraphTest(TestCase):
    def test_when_graph_for_non_augmented_grammar_then_error(self) -> None:
        grammar = Grammar(Rule('S', ['s']))
        self.assertRaises(AssertionError, graph_for, grammar)

    def test_given_single_rule_then_initial_and_final_state(self) -> None:
        from cmaj.testing.closure import closure
        grammar = Grammar(Rule('A', ['a']))
        v = [closure((1, 0, '$'), (0, 0, '$')),
             closure((1, 1, '$')),
             closure((0, 1, '$'))]
        e = [(0, 'A', 1), (0, 'a', 2)]
        self._given_grammar_then_correct_graph(grammar, 'A', v, e)

    def test_given_lr0_grammar_then_correct_graph(self) -> None:
        from cmaj.testing.closure import closure
        grammar = Grammar(Rule('A', ['1']), Rule('A', ['A', 'B']),
                          Rule('B', ['0']), Rule('B', ['1']))
        v = [closure((4, 0, '$'), (0, 0, '01$'), (1, 0, '01$')),
             closure((4, 1, '$'), (1, 1, '01$'), (2, 0, '01$'), (3, 0, '01$')),
             closure((0, 1, '01$')),
             closure((1, 2, '01$')),
             closure((2, 1, '01$')),
             closure((3, 1, '01$'))]
        e = [(0, 'A', 1), (0, '1', 2), (1, 'B', 3), (1, '0', 4), (1, '1', 5)]
        self._given_grammar_then_correct_graph(grammar, 'A', v, e)

    def test_given_slr_grammar_then_correct_graph(self) -> None:
        from cmaj.testing.closure import closure
        grammar = Grammar(Rule('S', ['X', 'X']),
                          Rule('X', ['a', 'X']), Rule('X', ['b']))
        v = [closure((3, 0, '$'), (0, 0, '$'), (1, 0, 'ab'), (2, 0, 'ab')),
             closure((3, 1, '$')),
             closure((0, 1, '$'), (1, 0, '$'), (2, 0, '$')),
             closure((1, 1, 'ab'), (1, 0, 'ab'), (2, 0, 'ab')),
             closure((2, 1, 'ab')),
             closure((0, 2, '$')),
             closure((1, 1, '$'), (1, 0, '$'), (2, 0, '$')),
             closure((2, 1, '$')),
             closure((1, 2, 'ab')),
             closure((1, 2, '$'))]
        e = [(0, 'S', 1), (0, 'X', 2), (0, 'a', 3), (0, 'b', 4),
             (2, 'X', 5), (2, 'a', 6), (2, 'b', 7),
             (3, 'X', 8), (3, 'a', 3), (3, 'b', 4),
             (6, 'X', 9), (6, 'a', 6), (6, 'b', 7)]
        self._given_grammar_then_correct_graph(grammar, 'S', v, e)

    def test_given_lr1_grammar_then_correct_graph(self) -> None:
        from cmaj.testing.closure import closure
        grammar = Grammar(Rule('A', ['B']), Rule('A', ['C', '1']),
                          Rule('B', ['C']),
                          Rule('C', ['0', 'B']))
        v = [closure((4, 0, '$'), (0, 0, '$'), (1, 0, '$'), (2, 0, '$'), (3, 0, '1$')),
             closure((4, 1, '$')),
             closure((0, 1, '$')),
             closure((1, 1, '$'), (2, 1, '$')),
             closure((3, 1, '1$'), (2, 0, '1$'), (3, 0, '1$')),
             closure((1, 2, '$')),
             closure((3, 2, '1$')),
             closure((2, 1, '1$'))]
        e = [(0, 'A', 1), (0, 'B', 2), (0, 'C', 3), (0, '0', 4),
             (3, '1', 5),
             (4, 'B', 6), (4, 'C', 7), (4, '0', 4)]
        self._given_grammar_then_correct_graph(grammar, 'A', v, e)

    def _given_grammar_then_correct_graph(self, grammar: Grammar, start: str,
                                          expected_closures: List[Closure],
                                          expected_edges: List[Tuple[int, str, int]]) -> None:
        from cmaj.parser.grammar import augment
        actual_graph = graph_for(augment(grammar, start))

        self.assertEqual(len(expected_closures), actual_graph.num_closures)
        self.assertEqual(len(expected_edges), actual_graph.num_edges)
        self.assertEqual(0, actual_graph.index(expected_closures[0]))  # Initial state contains start symbol.

        for c in expected_closures:
            self.assertIn(c, actual_graph.closures)

        for i, symbol, j in expected_edges:
            source = actual_graph.index(expected_closures[i])
            target = actual_graph.index(expected_closures[j])
            self.assertEqual(target, actual_graph.successor(source, symbol))
