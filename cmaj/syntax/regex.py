from typing import Optional, Callable

from cmaj.lexical.ast import Node
from cmaj.lexical.builder import AstBuilder
from cmaj.utils.regex import Regex


class NodeRegex(Regex):
    def __init__(self, identifier: Optional[str], regex: Regex, builder: AstBuilder):
        self._identifier = identifier
        self._regex = regex
        self._builder = builder

    def __call__(self, value: str) -> Optional[str]:
        node = Node(self._identifier)
        self._builder.enter_node(node)
        node.value = self._regex(value)
        self._builder.leave_node()
        return node.value


class RegexRef(Regex):
    def __init__(self, factory: Callable[[], Regex]):
        self._factory = factory

    def __call__(self, value: str) -> Optional[str]:
        regex = self._factory()
        return regex(value)
