from typing import List, Optional, Tuple


class Token(object):
    def __init__(self, line: int, column: int, value: str) -> None:
        self._line = line
        self._column = column
        self._value = value

    @property
    def line(self) -> int:
        return self._line

    @property
    def column(self) -> int:
        return self._column

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: 'Token') -> bool:
        return self._line == other._line and self._column == other._column and self._value == other._value

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class Node(object):
    def __init__(self, key: str, token: Optional[Token] = None) -> None:
        self._key: str = key
        self._token: Optional[Token] = token
        self._children: List[Node] = []

    @property
    def key(self) -> str:
        return self._key

    @property
    def token(self) -> Optional[Token]:
        return self._token

    @property
    def children(self) -> List['Node']:
        return list(self._children)

    def add_child(self, child: 'Node') -> None:
        assert self._token is None
        assert len(child) > 0
        self._children.append(child)

    def add_children(self, *children: 'Node') -> None:
        for child in children:
            self.add_child(child)

    def __len__(self) -> int:
        if not self._children and not self._token:
            return 0
        if self._token:
            return len(self._token.value)
        return end(self)[1] - begin(self)[1]

    def __eq__(self, other: 'Node') -> bool:
        return self._key == other._key \
               and self._token == other._token \
               and len(self._children) == len(other._children) \
               and self._children == other._children

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        hidden = set()
        if self._token is None:
            hidden.add('token')
        if not self._children:
            hidden.add('children')
        return stringify(self, hide=hidden)


def begin(node: Node) -> Tuple[int, int]:
    if node.token is not None:
        return node.token.line, node.token.column
    indexes = [begin(child) for child in node.children]
    max_line = max(line for line, _ in indexes)
    min_begin = min(column for line, column in indexes if line == max_line)
    return max_line, min_begin


def end(node: Node) -> Tuple[int, int]:
    if node.token is not None:
        return node.token.line, node.token.column + len(node.token.value)
    indexes = [end(child) for child in node.children]
    max_line = max(line for line, _ in indexes)
    max_end = max(column for line, column in indexes if line == max_line)
    return max_line, max_end
