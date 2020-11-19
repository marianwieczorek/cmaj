from typing import Any, Tuple

from cmaj.ast.node import Node, Token


def tree(tree_def: Tuple[Any, ...]) -> Node:
    key, token_or_children = tree_def
    if isinstance(token_or_children, Token):
        return Node(key, token=token_or_children)
    if isinstance(token_or_children, list):
        node = Node(key)
        node.add_children(*(tree(child) for child in token_or_children))
        return node
    raise TypeError(f'Unexpected type {type(token_or_children)!r}.')


def token(key: str, line: int) -> Tuple[str, Token]:
    return key, Token(line, 0, key.lower())
