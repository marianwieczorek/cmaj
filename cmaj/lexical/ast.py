from typing import Iterator, List, Optional


class Node(object):
    def __init__(self, key: str, value: Optional[str] = None, children: Optional[List['Node']] = None):
        self._key = key
        self._value = value
        self._parent: Optional[Node] = None
        self._children: List[Node] = children or []

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Optional[str]:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def parent(self) -> Optional['Node']:
        return self._parent

    def is_root(self) -> bool:
        return self._parent is None

    def detach(self):
        if self._parent is not None:
            self._parent.remove(self)

    def __iter__(self) -> Iterator['Node']:
        return iter(self._children)

    @property
    def children(self) -> List['Node']:
        return [child for child in self._children]

    def flatten(self) -> Iterator['Node']:
        yield self
        for child in self._children:
            for node in child.flatten():
                yield node

    def is_leaf(self) -> bool:
        return not self._children

    def add(self, child: 'Node'):
        if not child.is_root():
            child.detach()
        self._children.append(child)
        child._parent = self

    def remove(self, child: 'Node'):
        assert child in self._children
        self._children.remove(child)
        child._parent = None

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        custom_repr = {}
        hidden_fields = set()
        if self.is_root():
            hidden_fields.add('parent')
        else:
            custom_repr = {'parent': self._parent._key}
        if self.is_leaf():
            hidden_fields.add('children')
        return stringify(self, use=custom_repr, hide=hidden_fields)
