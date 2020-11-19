def load(path: str, separator: str) -> str:
    with open(path) as file:
        return separator.join(file.readlines())
