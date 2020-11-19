from unittest import TestCase

from cmaj.parser.grammar import Grammar, Rule


class RuleTest(TestCase):
    def test_given_none_as_key_then_error(self) -> None:
        self.assertRaises(AssertionError, Rule, None, ['a'])

    def test_given_none_as_symbol_then_error(self) -> None:
        self.assertRaises(AssertionError, Rule, 'A', [None])

    def test_given_empty_sequence_then_error(self) -> None:
        self.assertRaises(AssertionError, Rule, 'A', [])

    def test_given_sequence_with_epsilon_then_error(self) -> None:
        self.assertRaises(AssertionError, Rule, 'A', [''])
        self.assertRaises(AssertionError, Rule, 'A', ['a', ''])
        self.assertRaises(AssertionError, Rule, 'A', ['', 'a'])

    def test_given_recursion_without_production_then_error(self) -> None:
        self.assertRaises(AssertionError, Rule, 'A', ['A'])

    def test_given_equal_rules_then_equal(self) -> None:
        self.assertEqual(Rule('A', ['A', 'a']), Rule('A', ['A', 'a']))

    def test_given_rules_with_different_keys_then_not_equal(self) -> None:
        self.assertNotEqual(Rule('A', ['X']), Rule('B', ['X']))

    def test_given_rules_with_different_sequences_then_not_equal(self) -> None:
        self.assertNotEqual('A', ['X'], Rule('A', ['Y']))
        self.assertNotEqual('A', ['a'], Rule('A', ['a', 'a']))
        self.assertNotEqual('A', ['A', 'A'], Rule('A', ['A', 'a']))

    def test_given_equal_rules_then_same_hash(self) -> None:
        self.assertEqual(hash(Rule('A', ['a'])), hash(Rule('A', ['a'])))


class SymbolsTest(TestCase):
    def test_given_no_rules_then_empty(self) -> None:
        grammar = Grammar()
        self.assertEqual([], grammar.symbols)

    def test_given_only_references_then_references_in_order(self) -> None:
        grammar = Grammar(Rule('A', ['A', 'A']), Rule('B', ['B', 'B']))
        self.assertEqual(['A', 'B'], grammar.symbols)

    def test_given_references_and_terminals_then_references_terminals_in_order(self) -> None:
        grammar = Grammar(Rule('A', ['a', 'a']), Rule('B', ['b', 'a']))
        self.assertEqual(['A', 'B', 'a', 'b'], grammar.symbols)

    def test_given_reference_in_rules_then_order_of_rules_before_order_of_rule_symbols(self) -> None:
        grammar = Grammar(Rule('X', ['B', 'A', 'X']), Rule('A', ['a']), Rule('B', ['b']), Rule('X', ['x']))
        self.assertEqual(['X', 'A', 'B', 'a', 'b', 'x'], grammar.symbols)


class FirstTest(TestCase):
    def test_given_empty_list_then_empty(self) -> None:
        grammar = Grammar()
        first_set = grammar.first([])
        self.assertEqual(set(), first_set)

    def test_given_terminal_then_terminal(self) -> None:
        grammar = Grammar()
        first_set = grammar.first(['terminal'])
        self.assertEqual({'terminal'}, first_set)

    def test_given_many_terminals_then_first_terminal(self) -> None:
        grammar = Grammar(Rule('X', ['a']), Rule('X', ['b']))
        first_set = grammar.first(['x', 'a', 'b'])
        self.assertEqual({'x'}, first_set)

    def test_given_reference_then_first_terminals_of_references(self) -> None:
        grammar = Grammar(Rule('X', ['A']), Rule('A', ['a']), Rule('A', ['B']), Rule('B', ['b']))
        first_set = grammar.first(['X', 'x'])
        self.assertEqual({'a', 'b'}, first_set)

    def test_given_reference_with_recursion_then_non_recursive_terminals(self) -> None:
        grammar = Grammar(Rule('X', ['X', 'x']), Rule('X', ['A', 'x']), Rule('A', ['a', 'x']))
        first_set = grammar.first(['X'])
        self.assertEqual({'a'}, first_set)

    def test_given_cycle_then_first_cycle_breaking_terminals(self) -> None:
        grammar = Grammar(Rule('A', ['B']), Rule('A', ['a']), Rule('B', ['A']), Rule('B', ['b']))
        first_set = grammar.first(['A'])
        self.assertEqual({'a', 'b'}, first_set)


class AugmentTest(TestCase):
    def test_given_start_is_terminal_when_augment_then_error(self) -> None:
        from cmaj.parser.grammar import augment
        grammar = Grammar()
        self.assertRaises(AssertionError, augment, grammar, 'S')

    def test_given_augmented_start_in_grammar_when_augment_then_error(self) -> None:
        from cmaj.parser.grammar import augment
        grammar = Grammar(Rule('S', [Grammar.AUGMENTED_START]))
        self.assertRaises(AssertionError, augment, grammar, 'S')

    def test_given_augmented_eof_in_grammar_when_augment_then_error(self) -> None:
        from cmaj.parser.grammar import augment
        grammar = Grammar(Rule('S', [Grammar.AUGMENTED_EOF]))
        self.assertRaises(AssertionError, augment, grammar, 'S')

    def test_given_augmented_grammar_then_augmented_rule_is_last(self) -> None:
        from cmaj.parser.grammar import augment
        grammar = augment(Grammar(Rule('S', ['s'])), 'S')
        self.assertEqual(Rule(grammar.AUGMENTED_START, ['S']), grammar.rule_at(-1))
