from typing import Optional, Tuple, Union


class Regex(object):
    def __call__(self, values: str) -> Optional[str]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class Eq(Regex):
    def __init__(self, matcher: str) -> None:
        self._matcher = matcher

    def __call__(self, values: str) -> Optional[str]:
        return self._matcher if values.startswith(self._matcher) else None


StrOrRegex = Union[str, Regex]


class Maybe(Regex):
    def __init__(self, arg: StrOrRegex) -> None:
        self._regex = unpack_arg(arg)

    def __call__(self, values: str) -> str:
        return '' if (result := self._regex(values)) is None else result


class Repeat(Regex):
    def __init__(self, arg: StrOrRegex, at_least=0) -> None:
        self._regex = unpack_arg(arg)
        self._min_repeat = at_least

    def __call__(self, values: str) -> str:
        from typing import List
        parts: List[str] = []
        while (part := self._regex(values)) is not None:
            parts.append(part)
            values = values[len(part):]
        return None if len(parts) < self._min_repeat else ''.join(parts)


class FirstOf(Regex):
    def __init__(self, *args: StrOrRegex) -> None:
        self._regex_list = unpack_args(*args)

    def __call__(self, values: str) -> Optional[str]:
        for regex in self._regex_list:
            if (result := regex(values)) is not None:
                return result
        return None


class Seq(Regex):
    def __init__(self, *args: StrOrRegex) -> None:
        self._regex_list = unpack_args(*args)

    def __call__(self, values: str) -> Optional[str]:
        result = ''
        for regex in self._regex_list:
            if (part := regex(values)) is None:
                return None
            result += part
            values = values[len(part):]
        return result


def unpack_args(*args: Union[str, Regex]) -> Tuple[Regex]:
    return tuple(unpack_arg(str_or_regex) for str_or_regex in args)


def unpack_arg(arg: Union[str, Regex]) -> Regex:
    if isinstance(arg, Regex):
        return arg
    elif isinstance(arg, str):
        return Eq(arg)
    raise TypeError(f'Expected str or Regex but was: {type(arg)!r}')
