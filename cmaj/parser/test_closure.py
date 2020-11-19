from unittest import TestCase

from cmaj.parser.closure import RuleState, closure_for, resolve
from cmaj.parser.grammar import Grammar, Rule


class RuleStateTest(TestCase):
    def test_given_no_lookaheads_then_error(self) -> None:
        self.assertRaises(AssertionError, RuleState, 0, 0, set())

    def test_given_empty_lookahead_then_error(self) -> None:
        self.assertRaises(AssertionError, RuleState, 0, 0, {''})

    def test_given_equal_states_then_equal(self) -> None:
        self.assertEqual(RuleState(0, 0, {'x'}), RuleState(0, 0, {'x'}))
        self.assertEqual(RuleState(1, 2, {'3', '4'}), RuleState(1, 2, {'3', '4'}))

    def test_given_different_rule_index_then_not_equal(self) -> None:
        self.assertNotEqual(RuleState(0, 2, {'3', '4'}), RuleState(1, 2, {'3', '4'}))

    def test_given_different_num_processed_then_not_equal(self) -> None:
        self.assertNotEqual(RuleState(1, 0, {'3', '4'}), RuleState(1, 2, {'3', '4'}))

    def test_given_different_lookaheads_then_not_equal(self) -> None:
        self.assertNotEqual(RuleState(1, 2, {'3'}), RuleState(1, 2, {'3', '4'}))
        self.assertNotEqual(RuleState(1, 2, {'0', '4'}), RuleState(1, 2, {'3', '4'}))

    def test_given_equal_states_then_same_hash(self) -> None:
        self.assertEqual(hash(RuleState(1, 2, {'3', '4'})), hash(RuleState(1, 2, {'3', '4'})))


class FollowStatesTest(TestCase):
    def test_given_unprocessed_terminal_then_no_follow_states(self) -> None:
        grammar = Grammar(Rule('A', ['a']))
        state = RuleState(0, 0, {'a'})
        self.assertEqual(set(), state.follow_states(grammar))

    def test_given_unprocessed_reference_then_initial_reference_states(self) -> None:
        grammar = Grammar(Rule('A', ['B']), Rule('B', ['b']))
        state = RuleState(0, 0, {'b'})
        self.assertEqual({RuleState(1, 0, {'b'})}, state.follow_states(grammar))

    def test_given_last_unprocessed_reference_then_lookaheads_of_parent(self) -> None:
        grammar = Grammar(Rule('A', ['x', 'B']), Rule('A', ['B', 'x']), Rule('B', ['x']))
        state = RuleState(0, 1, {'a'})
        self.assertEqual({RuleState(2, 0, {'a'})}, state.follow_states(grammar))

    def test_given_reference_followed_by_terminal_then_lookahead_is_terminal(self) -> None:
        grammar = Grammar(Rule('A', ['B', 'a']), Rule('B', ['x']))
        state = RuleState(0, 0, {'x'})
        self.assertEqual({RuleState(1, 0, {'a'})}, state.follow_states(grammar))

    def test_given_reference_followed_by_reference_then_lookahead_is_first_set(self) -> None:
        grammar = Grammar(Rule('A', ['B', 'X']), Rule('B', ['x']), Rule('X', ['a']), Rule('X', ['b']))
        state = RuleState(0, 0, {'x'})
        self.assertEqual({RuleState(1, 0, {'a', 'b'})}, state.follow_states(grammar))

    def test_given_reference_followed_by_recursion_then_lookahead_is_first_set(self) -> None:
        grammar = Grammar(Rule('X', ['a']), Rule('X', ['b', 'X', 'X']))
        state = RuleState(1, 1, {'x'})
        expected = {RuleState(0, 0, {'a', 'b'}), RuleState(1, 0, {'a', 'b'})}
        self.assertEqual(expected, state.follow_states(grammar))


class ResolvedRuleStateTest(TestCase):
    def test_given_unprocessed_terminal_then_not_reducible_and_next_symbol_is_terminal(self) -> None:
        grammar = Grammar(Rule('A', ['a', 'A']))
        state = resolve(RuleState(0, 0, {'$'}), grammar)
        self.assertFalse(state.reducible)
        self.assertEqual('a', state.next_symbol)

    def test_given_unprocessed_reference_then_not_reducible_and_next_symbol_is_reference(self) -> None:
        grammar = Grammar(Rule('A', ['a', 'A']))
        state = resolve(RuleState(0, 1, {'$'}), grammar)
        self.assertFalse(state.reducible)
        self.assertEqual('A', state.next_symbol)

    def test_given_processed_rule_then_reducible(self) -> None:
        grammar = Grammar(Rule('A', ['a', 'A']))
        state = resolve(RuleState(0, 2, {'$'}), grammar)
        self.assertTrue(state.reducible)


class ClosureTest(TestCase):
    def test_given_grammar_with_single_rule_then_complete_closure(self) -> None:
        grammar = Grammar(Rule('X', ['x']))
        result = closure_for(grammar, RuleState(0, 0, {'$'}))
        self.assertEqual({RuleState(0, 0, {'$'})}, result)

    def test_given_states_followed_by_terminals_then_complete_closure(self) -> None:
        grammar = Grammar(Rule('A', ['X', 'a']), Rule('A', ['A', 'X']), Rule('X', ['x']))
        result = closure_for(grammar, RuleState(0, 1, {'$'}), RuleState(1, 2, {'$'}))
        self.assertEqual({RuleState(0, 1, {'$'}), RuleState(1, 2, {'$'})}, result)

    def test_given_states_followed_by_references_then_closure_includes_references(self) -> None:
        grammar = Grammar(Rule('A', ['x', 'B']), Rule('B', ['C']), Rule('C', ['x']))
        result = closure_for(grammar, RuleState(0, 1, {'$'}))
        expected = {RuleState(0, 1, {'$'}), RuleState(1, 0, {'$'}), RuleState(2, 0, {'$'})}
        self.assertEqual(expected, result)

    def test_given_state_followed_by_two_references_then_lookahead_of_reference(self) -> None:
        grammar = Grammar(Rule('A', ['B', 'B']), Rule('B', ['b']))
        result = closure_for(grammar, RuleState(0, 0, {'$'}))
        self.assertEqual({RuleState(0, 0, {'$'}), RuleState(1, 0, {'b'})}, result)

    def test_given_states_followed_by_recursion_then_closure_includes_all_lookaheads(self) -> None:
        grammar = Grammar(Rule('A', ['a', 'A']), Rule('A', ['A', 'A']))
        result = closure_for(grammar, RuleState(0, 1, {'$'}))
        expected = {RuleState(0, 1, {'$'}), RuleState(1, 0, {'$', 'a'}), RuleState(0, 0, {'$', 'a'})}
        self.assertEqual(expected, result)

    def test_given_states_in_cycles_then_closure_includes_all_lookaheads(self) -> None:
        grammar = Grammar(Rule('C', ['A']), Rule('A', ['B', 'B']), Rule('B', ['C']),
                          Rule('C', ['c']), Rule('A', ['a']), Rule('B', ['b']))
        result = closure_for(grammar, RuleState(1, 1, {'$'}))
        expected = {RuleState(1, 1, {'$'}),
                    RuleState(2, 0, {'$', 'c', 'a', 'b'}), RuleState(5, 0, {'$', 'c', 'a', 'b'}),
                    RuleState(0, 0, {'$', 'c', 'a', 'b'}), RuleState(3, 0, {'$', 'c', 'a', 'b'}),
                    RuleState(1, 0, {'$', 'c', 'a', 'b'}), RuleState(4, 0, {'$', 'c', 'a', 'b'})}
        self.assertEqual(expected, result)

    def test_given_lookaheads_then_closure_simplifies_lookaheads(self) -> None:
        grammar = Grammar(Rule('A', ['a']), Rule('A', ['B', 'B']), Rule('B', ['b']), Rule('B', ['A', 'B']))
        result = closure_for(grammar, RuleState(1, 1, {'x', 'y'}))
        expected = {RuleState(1, 1, {'x', 'y'}),
                    RuleState(2, 0, {'x', 'y', 'b', 'a'}), RuleState(3, 0, {'x', 'y', 'b', 'a'}),
                    RuleState(0, 0, {'b', 'a'}), RuleState(1, 0, {'b', 'a'})}
        self.assertEqual(expected, result)
