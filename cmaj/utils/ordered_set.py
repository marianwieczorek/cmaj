from typing import Iterator, Sequence, TypeVar, overload

T = TypeVar('T')


class OrderedSet(Sequence[T]):
    def __init__(self, *values: T) -> None:
        self._value_list = tuple(dict.fromkeys(values))
        self._value_set = frozenset(values)

    def __len__(self) -> int:
        return len(self._value_list)

    def __contains__(self, value: T) -> bool:
        return value in self._value_set

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, slice_: slice) -> 'OrderedSet[T]':
        ...

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._value_list[key]
        if isinstance(key, slice):
            return OrderedSet(*self._value_list[key])
        raise TypeError(f'Invalid key type. Expected int or slice but was: {type(key)}')

    def __iter__(self) -> Iterator[T]:
        return iter(self._value_list)

    def __ror__(self, lhs: Sequence[T]) -> 'OrderedSet[T]':
        return OrderedSet(*lhs, *self)

    def __or__(self, rhs: Sequence[T]) -> 'OrderedSet[T]':
        return OrderedSet(*self, *rhs)

    def __eq__(self, other: 'OrderedSet[T]') -> bool:
        return self._value_list == other._value_list

    def __hash__(self) -> int:
        return hash(self._value_list)

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self, hide={'value_set'})
