from typing import Optional, Set

from cmaj.lexical.ast import Node


class AstBuilder(object):

    def __init__(self):
        self._node: Optional[Node] = None
        self._ast: Set[Node] = set()

    def build(self) -> Optional[Node]:
        assert self._node is None
        if not self._ast:
            return None
        root = next(node for node in self._ast if node.is_root())
        self._ast.clear()
        return _simplify(root)

    def enter_node(self, node: Node):
        assert node not in self._ast
        if self._node is not None:
            self._node.add(node)
        self._ast.add(node)
        self._node = node

    def leave_node(self):
        assert self._node is not None
        child = self._node
        self._node = self._node.parent
        if child.value is None:
            self._prune(child)

    def _prune(self, node: Node):
        node.detach()
        for n in node.flatten():
            self._ast.remove(n)

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


def _simplify(root: Node) -> Node:
    node = Node(root.key, root.value)
    child_gen = (_simplify(child) for child in root)
    child_gen = (child.children if child.key is None else [child] for child in child_gen)
    child_gen = (child for children in child_gen for child in children)
    for child in child_gen:
        node.add(child)
    return node
