from typing import Tuple

from cmaj.parser.closure import Closure, RuleState
from cmaj.parser.grammar import Grammar
from cmaj.parser.graph import ClosureGraph


def to_string(graph: ClosureGraph, grammar: Grammar) -> str:
    from typing import List
    results: List[str] = []
    for index, closure in enumerate(graph.closures):
        results.append(_closure_to_string(index, closure, grammar))
    return '\n\n'.join(results)


def _closure_to_string(index: int, closure: Closure, grammar: Grammar) -> str:
    from typing import List
    lines: List[Tuple[str, str, str]] = []
    widths = (0, 0, 0, 0)
    for rule_state in sorted(closure, key=lambda r: r.rule_index):
        line = _rule_state_to_string(rule_state, grammar)
        lines.append(line)
        widths = tuple(max(max_width, len(value)) for max_width, value in zip(widths, line))

    result = '\n'.join([f'    {line[0]:{widths[0]}} -> {line[1]:{widths[1]}} | {line[2]}' for line in lines])
    return f'CLOSURE {index}:\n{result}'


def _rule_state_to_string(rule_state: RuleState, grammar: Grammar) -> Tuple[str, str, str]:
    rule = grammar.rule_at(rule_state.rule_index)
    key = rule.key
    processed_str = ' '.join(rule.symbols[:rule_state.num_processed])
    unprocessed_str = ' '.join(rule.symbols[rule_state.num_processed:])
    lookaheads_str = ' '.join([str(symbol) for symbol in rule_state.lookaheads])
    return f'{key}', f'{processed_str}⬤{unprocessed_str}', f'{lookaheads_str}'
