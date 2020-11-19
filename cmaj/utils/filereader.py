from typing import List


def read(filename: str) -> List[str]:
    with open(filename) as file:
        return file.readlines()
