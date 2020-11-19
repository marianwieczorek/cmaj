from typing import Tuple

from cmaj.parser.closure import Closure


def closure(*states: Tuple[int, int, str]) -> Closure:
    from typing import FrozenSet
    from cmaj.parser.closure import RuleState
    from cmaj.parser.grammar import Grammar

    def unpack_lookaheads(terminals: str) -> FrozenSet[str]:
        return frozenset({Grammar.AUGMENTED_EOF if ch == '$' else ch for ch in terminals})

    return frozenset({RuleState(rule_index, num_processed, unpack_lookaheads(lookaheads))
                      for rule_index, num_processed, lookaheads in states})
