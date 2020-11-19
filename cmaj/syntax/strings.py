from typing import List


def expand(begin: str, end: str) -> List[str]:
    assert len(begin) == 1
    assert len(end) == 1
    assert begin <= end
    value = ''.join(chr(value) for value in range(ord(begin), ord(end) + 1))
    return [*value]
