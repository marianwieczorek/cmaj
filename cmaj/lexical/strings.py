from typing import List


def expand(begin: str, end: str, exclude: str = None) -> List[str]:
    assert len(begin) == 1
    assert len(end) == 1
    assert exclude is None or len(exclude) == 1

    if begin > end:
        return expand(end, begin, exclude=exclude)
    return [chr(ch) for ch in range(ord(begin), ord(end) + 1) if chr(ch) != exclude]
