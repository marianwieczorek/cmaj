from typing import List, Optional

from cmaj.ast.node import Node
from cmaj.lexical.regex import Regex


class ScannerError(Exception):
    def __init__(self, line_index: int, column_index: int, message: str) -> None:
        super().__init__(f'{line_index}:{column_index} {message}')


class Matcher(object):
    def __init__(self, key: str, regex: Regex) -> None:
        self._key = key
        self._regex = regex

    def match(self, line_index: int, column_index: int, sequence: str) -> Optional[Node]:
        from cmaj.ast.node import Token
        if (result := self._regex(sequence)) is not None:
            return Node(self._key, token=Token(line_index, column_index, result))
        return None

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


def scan(lines: List[str], matchers: List[Matcher]) -> List[Node]:
    return [node for index, line in enumerate(lines) for node in scan_line(index, line, matchers)]


def scan_line(line_index: int, line: str, matchers: List[Matcher]) -> List[Node]:
    nodes = []
    column_index = 0
    while column_index < len(line):
        node = scan_next(line_index, column_index, line[column_index:], matchers)
        nodes.append(node)
        column_index += len(node)
    return nodes


def scan_next(line_index: int, column_index: int, sequence: str, matchers: List[Matcher]) -> Node:
    for matcher in matchers:
        if (node := matcher.match(line_index, column_index, sequence)) is not None:
            assert len(node) > 0
            return node
    raise ScannerError(line_index, column_index, f'Unexpected token: {sequence[0]!r}')
