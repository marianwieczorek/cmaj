from typing import Optional
from unittest import TestCase

from cmaj.parser.grammar import Grammar, Rule
from cmaj.parser.graph import ClosureGraph
from cmaj.parser.table import Action, ConflictError, table_for


class TableSizeTest(TestCase):
    def test_given_non_lr1_when_collision_then_error(self) -> None:
        from cmaj.parser.grammar import augment
        from cmaj.parser.graph import graph_for
        grammar = Grammar(Rule('X', ['0', 'X', '0']), Rule('X', ['1', 'X', '1']), Rule('X', ['0']), Rule('X', ['1']))
        grammar = augment(grammar, 'X')
        graph = graph_for(grammar)
        self.assertRaises(ConflictError, table_for, grammar, graph)

    def test_given_empty_grammar_and_graph_then_empty_table(self) -> None:
        table = table_for(Grammar(), ClosureGraph())
        self.assertEqual(0, table.num_rows)
        self.assertEqual(1, table.num_columns)

    def test_given_grammar_and_graph_then_table_with_num_closures_rows_and_num_symbols_columns(self) -> None:
        from cmaj.parser.grammar import augment
        from cmaj.testing.closure import closure
        grammar = augment(Grammar(Rule('A', ['a']), Rule('B', ['b'])), 'A')

        graph = ClosureGraph()
        c1 = closure((0, 0, '$'))
        c2 = closure((1, 0, '$'))
        graph.add_edge(c1, 'a', c2)
        graph.add_edge(c2, 'b', c1)

        table = table_for(grammar, graph)
        self.assertEqual(2, table.num_rows)
        self.assertEqual(5, table.num_columns)

    def test_given_slr_grammar_then_correct_table(self) -> None:
        from cmaj.parser.grammar import augment
        from cmaj.parser.graph import graph_for
        grammar = augment(Grammar(Rule('S', ['X', 'X']), Rule('X', ['a', 'X']), Rule('X', ['b'])), 'S')
        graph = graph_for(grammar)
        table = table_for(grammar, graph)

        s = [row_of(graph, 0, 0, Grammar.AUGMENTED_EOF),
             row_of(graph, 3, 1, Grammar.AUGMENTED_EOF),
             row_of(graph, 0, 1, Grammar.AUGMENTED_EOF),
             row_of(graph, 1, 1, 'a'),
             row_of(graph, 2, 1, 'a'),
             row_of(graph, 0, 2, Grammar.AUGMENTED_EOF),
             row_of(graph, 1, 1, Grammar.AUGMENTED_EOF),
             row_of(graph, 2, 1, Grammar.AUGMENTED_EOF),
             row_of(graph, 1, 2, 'a'),
             row_of(graph, 1, 2, Grammar.AUGMENTED_EOF)]

        count = sum(1 for row in range(10) for column in ['S', 'X', 'a', 'b', Grammar.AUGMENTED_EOF]
                    if table.action(row, column) is None)
        self.assertEqual(29, count)

        self.assertEqual(Action.shift(s[3]), table.action(s[0], 'a'))
        self.assertEqual(Action.shift(s[4]), table.action(s[0], 'b'))
        self.assertEqual(Action.goto(s[1]), table.action(s[0], 'S'))
        self.assertEqual(Action.goto(s[2]), table.action(s[0], 'X'))

        self.assertEqual(Action.accept(3), table.action(s[1], Grammar.AUGMENTED_EOF))

        self.assertEqual(Action.shift(s[6]), table.action(s[2], 'a'))
        self.assertEqual(Action.shift(s[7]), table.action(s[2], 'b'))
        self.assertEqual(Action.goto(s[5]), table.action(s[2], 'X'))

        self.assertEqual(Action.shift(s[3]), table.action(s[3], 'a'))
        self.assertEqual(Action.shift(s[4]), table.action(s[3], 'b'))
        self.assertEqual(Action.goto(s[8]), table.action(s[3], 'X'))

        self.assertEqual(Action.reduce(2), table.action(s[4], 'a'))
        self.assertEqual(Action.reduce(2), table.action(s[4], 'b'))

        self.assertEqual(Action.reduce(0), table.action(s[5], Grammar.AUGMENTED_EOF))

        self.assertEqual(Action.shift(s[6]), table.action(s[6], 'a'))
        self.assertEqual(Action.shift(s[7]), table.action(s[6], 'b'))
        self.assertEqual(Action.goto(s[9]), table.action(s[6], 'X'))

        self.assertEqual(Action.reduce(2), table.action(s[7], Grammar.AUGMENTED_EOF))

        self.assertEqual(Action.reduce(1), table.action(s[8], 'a'))
        self.assertEqual(Action.reduce(1), table.action(s[8], 'b'))

        self.assertEqual(Action.reduce(1), table.action(s[9], Grammar.AUGMENTED_EOF))


def row_of(graph: ClosureGraph, rule_index: int, num_processed: int, lookahead: Optional[str]) -> int:
    for index, closure in enumerate(graph.closures):
        for rule_state in closure:
            if rule_state.rule_index == rule_index and \
                    rule_state.num_processed == num_processed and \
                    lookahead in rule_state.lookaheads:
                return index
    raise IndexError(f'No closure for ({rule_index}, {num_processed}, {lookahead!r}).')
