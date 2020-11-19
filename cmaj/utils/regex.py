from typing import Optional, Union


class Regex(object):
    def __call__(self, value: str) -> Optional[str]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class Eq(Regex):
    def __init__(self, matcher: str):
        self._matcher = matcher

    def __call__(self, value: str) -> Optional[str]:
        size = len(self._matcher)
        segment = None if len(value) < size else value[:size]
        return segment if self._matcher == segment else None


TupleOrRegexOrMatcher = Union[tuple, Regex, str]


class Maybe(Regex):
    def __init__(self, arg: TupleOrRegexOrMatcher):
        self._regex = unpack_arg(arg)

    def __call__(self, value: str) -> Optional[str]:
        result = self._regex(value)
        return '' if result is None else result


class FirstOf(Regex):
    def __init__(self, *args: TupleOrRegexOrMatcher):
        self._regex_list = tuple(unpack_arg(arg) for arg in args)

    def __call__(self, value: str) -> Optional[str]:
        for regex in self._regex_list:
            if (result := regex(value)) is not None:
                return result
        return None


class Repeat(Regex):
    def __init__(self, arg: TupleOrRegexOrMatcher):
        self._regex = unpack_arg(arg)

    def __call__(self, value: str) -> Optional[str]:
        results = []
        index = 0
        while (result := self._regex(value[index:])) is not None:
            assert len(result) > 0
            results.append(result)
            index += len(result)
        return ''.join(results)


class Seq(Regex):
    def __init__(self, *args: TupleOrRegexOrMatcher):
        self._regex_list = tuple(unpack_arg(arg) for arg in args)

    def __call__(self, value: str) -> Optional[str]:
        results = []
        index = 0
        for regex in self._regex_list:
            if (result := regex(value[index:])) is None:
                return None
            results.append(result)
            index += len(result)
        return ''.join(results)


def unpack_arg(arg: TupleOrRegexOrMatcher) -> Regex:
    if isinstance(arg, tuple):
        return Seq(*(unpack_arg(arg_item) for arg_item in arg))
    if isinstance(arg, Regex):
        return arg
    elif isinstance(arg, str):
        return Eq(arg)
    raise TypeError(f'Unexpected argument type: {type(arg)}')
