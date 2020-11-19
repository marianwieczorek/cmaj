from typing import AbstractSet, FrozenSet, List, Mapping

from cmaj.parser.grammar import Grammar


class RuleState(object):
    @staticmethod
    def start(grammar: Grammar) -> 'RuleState':
        assert grammar.is_augmented
        return RuleState(len(grammar) - 1, 0, {Grammar.AUGMENTED_EOF})

    def __init__(self, rule_index: int, num_processed: int, lookaheads: AbstractSet[str]) -> None:
        assert lookaheads
        assert all(lookaheads)
        self._rule_index = rule_index
        self._num_processed = num_processed
        self._lookaheads = frozenset(lookaheads)

    @property
    def rule_index(self) -> int:
        return self._rule_index

    @property
    def num_processed(self) -> int:
        return self._num_processed

    @property
    def lookaheads(self) -> FrozenSet[str]:
        return self._lookaheads

    def follow_states(self, grammar: Grammar) -> FrozenSet['RuleState']:
        if (state := ResolvedRuleState(self, grammar)).reducible:
            return frozenset()
        follow_lookaheads = grammar.first(state.follow_symbols) or self._lookaheads
        follow_indexes = grammar.indexes_of(state.next_symbol)
        return frozenset({RuleState(index, 0, follow_lookaheads) for index in follow_indexes})

    def __eq__(self, other: 'RuleState') -> bool:
        return self._rule_index == other._rule_index and \
               self._num_processed == other._num_processed and \
               self._lookaheads == other._lookaheads

    def __hash__(self) -> int:
        index_hash = self._num_processed + 7 * self._rule_index
        return index_hash

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class ResolvedRuleState(object):
    def __init__(self, state: RuleState, grammar: Grammar) -> None:
        rule = grammar.rule_at(state.rule_index)
        self._key = rule.key
        self._unprocessed_symbols = rule.symbols[state.num_processed:]

    @property
    def key(self) -> str:
        return self._key

    @property
    def reducible(self) -> bool:
        return not self._unprocessed_symbols

    @property
    def next_symbol(self) -> str:
        return self._unprocessed_symbols[0]

    @property
    def follow_symbols(self) -> List[str]:
        return self._unprocessed_symbols[1:]

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


def resolve(state: RuleState, grammar: Grammar) -> ResolvedRuleState:
    return ResolvedRuleState(state, grammar)


Closure = FrozenSet[RuleState]


def closure_for(grammar: Grammar, *states: RuleState) -> Closure:
    closure = _closure_for(grammar, set(states), set())
    return _simplify_lookaheads(closure)


def _closure_for(grammar: Grammar,
                 states: AbstractSet[RuleState],
                 visited: AbstractSet[RuleState]) -> FrozenSet[RuleState]:
    new_states = frozenset.union(*(state.follow_states(grammar) for state in states)) - visited
    if not new_states:
        return frozenset(states)
    return frozenset(states) | _closure_for(grammar, new_states, visited | new_states)


def _simplify_lookaheads(closure: Closure) -> Closure:
    from collections import defaultdict
    from typing import Dict, Set, Tuple
    simplified: Dict[Tuple[int, int], Set[str]] = defaultdict(set)
    for rule_state in closure:
        simplified[(rule_state.rule_index, rule_state.num_processed)] |= rule_state.lookaheads
    return frozenset({RuleState(rule_index, num_processed, lookaheads)
                      for (rule_index, num_processed), lookaheads in simplified.items()})


def successors_for(grammar: Grammar, closure: Closure) -> Mapping[str, Closure]:
    from collections import defaultdict
    from typing import Dict, Set
    groups: Dict[str, Set[RuleState]] = defaultdict(set)
    for state in closure:
        resolved = ResolvedRuleState(state, grammar)
        if not resolved.reducible:
            symbol = resolved.next_symbol
            groups[symbol].add(RuleState(state.rule_index, state.num_processed + 1, state.lookaheads))
    return {key: closure_for(grammar, *value) for key, value in groups.items()}
