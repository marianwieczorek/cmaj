from typing import AbstractSet, FrozenSet, List


class Rule(object):
    def __init__(self, key: str, symbols: List[str]) -> None:
        assert key is not None
        assert symbols
        assert all(symbols)
        assert symbols != [key]
        self._key = key
        self._symbols = tuple(symbols)

    @property
    def key(self) -> str:
        return self._key

    @property
    def symbols(self) -> List[str]:
        return list(self._symbols)

    def __eq__(self, other: 'Rule') -> bool:
        return self._key == other._key and self._symbols == other._symbols

    def __hash__(self) -> int:
        return hash(self._key) ^ hash(self._symbols)

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class Grammar(object):
    AUGMENTED_START = '$start$'  # Key of start rule
    AUGMENTED_EOF = '$eof$'  # Terminal symbol for end-of-file

    def __init__(self, *rules: Rule) -> None:
        from cmaj.utils.ordered_set import OrderedSet
        self._rules = OrderedSet(*rules)

    def __len__(self) -> int:
        return len(self._rules)

    @property
    def symbols(self) -> List[str]:
        lhs_symbols = {rule.key: None for rule in self._rules}
        rhs_symbols = {symbol: None for rule in self._rules for symbol in rule.symbols}
        return list({**lhs_symbols, **rhs_symbols})

    def rule_at(self, index: int) -> Rule:
        return self._rules[index]

    @property
    def rules(self) -> List[Rule]:
        return list(self._rules)

    def rules_of(self, key: str) -> List[Rule]:
        return [rule for rule in self._rules if rule.key == key]

    def indexes_of(self, key: str) -> List[int]:
        return [index for index, rule in enumerate(self._rules) if rule.key == key]

    @property
    def is_augmented(self) -> bool:
        if not self._rules:
            return False
        return self._rules[-1].key == self.AUGMENTED_START

    def is_terminal(self, symbol: str) -> bool:
        return not self.rules_of(symbol)

    def first(self, symbols: List[str]) -> FrozenSet[str]:
        if not symbols:
            return frozenset()
        return self._first(symbols, set())

    def _first(self, symbols: List[str], visited: AbstractSet[str]) -> FrozenSet[str]:
        if (symbol := symbols[0]) in visited:
            return frozenset()
        if self.is_terminal(symbol):
            return frozenset({symbol})
        return frozenset.union(*(self._first(rule.symbols, visited | {symbol}) for rule in self.rules_of(symbol)))

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self, use={'rules': [*self._rules]})


def augment(grammar: Grammar, start: str) -> Grammar:
    assert not grammar.is_terminal(start)
    assert Grammar.AUGMENTED_START not in grammar.symbols
    assert Grammar.AUGMENTED_EOF not in grammar.symbols

    augmented_rules = grammar.rules + [Rule(Grammar.AUGMENTED_START, [start])]
    return Grammar(*augmented_rules)
