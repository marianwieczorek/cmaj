from typing import List, Optional

from cmaj.parser.grammar import Grammar
from cmaj.parser.graph import ClosureGraph


class ConflictError(Exception):
    pass


class Action(object):
    ACCEPT = 'accept'
    REDUCE = 'reduce'
    SHIFT = 'shift'
    GOTO = 'goto'

    @staticmethod
    def accept(rule_index: int) -> 'Action':
        return Action(Action.ACCEPT, rule_index)

    @staticmethod
    def reduce(rule_index: int) -> 'Action':
        return Action(Action.REDUCE, rule_index)

    @staticmethod
    def shift(state_index: int) -> 'Action':
        return Action(Action.SHIFT, state_index)

    @staticmethod
    def goto(state_index: int) -> 'Action':
        return Action(Action.GOTO, state_index)

    def __init__(self, key: str, index: int) -> None:
        self._key = key
        self._index = index

    @property
    def key(self) -> str:
        return self._key

    @property
    def index(self) -> int:
        return self._index

    def __eq__(self, other: 'Action') -> bool:
        return self._key == other._key and self._index == other._index

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class ParseTable(object):
    def __init__(self, num_closures: int, symbols: List[str]) -> None:
        from typing import Dict
        self._table: Dict[str, List[Optional[Action]]] = {symbol: num_closures * [None]
                                                          for symbol in symbols + [Grammar.AUGMENTED_EOF]
                                                          if symbol != Grammar.AUGMENTED_START}

    @property
    def num_rows(self) -> int:
        return len(self._table[Grammar.AUGMENTED_EOF])

    @property
    def num_columns(self) -> int:
        return len(self._table)

    def action(self, row: int, column: str) -> Action:
        return self._table[column][row]

    def set_action(self, row: int, column: str, action: Action) -> None:
        current_action = self._table[column][row]
        if current_action is None or current_action == action:
            self._table[column][row] = action
        else:
            raise ConflictError(f'Actions for state {row} and symbol {column!r} are {current_action!r} and {action!r}.')

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


def table_for(grammar: Grammar, graph: ClosureGraph) -> ParseTable:
    from cmaj.parser.closure import resolve
    table = ParseTable(graph.num_closures, grammar.symbols)
    it = ((row, state) for row, closure in enumerate(graph.closures) for state in closure)
    for row, state in it:
        resolved = resolve(state, grammar)
        if resolved.reducible and resolved.key == Grammar.AUGMENTED_START:
            table.set_action(row, Grammar.AUGMENTED_EOF, Action.accept(state.rule_index))
        elif resolved.reducible:
            for column in state.lookaheads:
                table.set_action(row, column, Action.reduce(state.rule_index))
        elif grammar.is_terminal(column := resolved.next_symbol):
            table.set_action(row, column, Action.shift(graph.successor(row, column)))
        else:
            table.set_action(row, column, Action.goto(graph.successor(row, column)))
    return table
