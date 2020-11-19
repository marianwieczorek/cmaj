from typing import List, Tuple

from cmaj.ast.node import Node
from cmaj.parser.grammar import Grammar, Rule
from cmaj.parser.table import ParseTable


class ParserError(Exception):
    pass


Stack = List[Tuple[int, Node]]


def parse(tokens: List[Node], grammar: Grammar, table: ParseTable) -> Node:
    from cmaj.parser.table import Action
    assert table.num_rows > 0
    stack: Stack = []
    row = 0
    tokens = tokens + [Node(Grammar.AUGMENTED_EOF)]
    token_index = 0
    while True:
        token = tokens[token_index]
        action = table.action(row, token.key)
        if action is None:
            raise ParserError(f'Unexpected token: {tokens[token_index]!r}')
        elif action.key == Action.ACCEPT:
            break
        elif action.key == Action.SHIFT:
            stack.append((row, tokens[token_index]))
            row = action.index
            token_index += 1
        elif action.key == Action.GOTO:
            row = action.index
        elif action.key == Action.REDUCE:
            rule_index = action.index
            rule = grammar.rule_at(rule_index)

            stack, row, nodes = _reduce_stack(stack, rule)
            node = _reduce_nodes(nodes, rule)
            stack.append((row, node))

            action = table.action(row, node.key)
            assert action.key == Action.GOTO
            row = action.index
        else:
            raise ParserError(f'Unexpected parser action {action!r} for token: {tokens[token_index]!r}')

    if len(stack) != 1:
        raise ParserError(f'Found unprocessed tokens: {_to_symbols(stack)!r}')
    return stack[0][1]


def _reduce_stack(stack: Stack, rule: Rule) -> Tuple[Stack, int, List[Node]]:
    num_symbols = len(rule.symbols)
    if num_symbols > len(stack):
        raise ParserError(f'Unable to apply rule {rule!r}. Too few tokens: {_to_symbols(stack)!r}')

    stack_tail, stack_head = stack[:-num_symbols], stack[-num_symbols:]
    row = stack_head[0][0]
    nodes = [node for _, node in stack_head]
    return stack_tail, row, nodes


def _reduce_nodes(nodes: List[Node], rule: Rule) -> Node:
    node = Node(rule.key)
    for symbol, child in zip(rule.symbols, nodes):
        if symbol != child.key:
            raise ParserError(f'Unable to apply rule {rule!r}. Unexpected token: {child!r}')
        node.add_child(child)
    return node


def _to_symbols(stack: Stack) -> List[str]:
    return [node.key for _, node in stack]
