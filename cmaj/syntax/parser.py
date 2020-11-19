from typing import Dict, List, Mapping, Optional, Set

from cmaj.lexical.ast import Node
from cmaj.lexical.builder import AstBuilder
from cmaj.syntax.regex import NodeRegex, RegexRef
from cmaj.utils.regex import Eq, FirstOf, Maybe, Regex, Repeat, Seq


class DefError(Exception):
    def __init__(self, message: str, line: Optional[int] = None):
        if line is None:
            msg = message
        else:
            msg = f'Line {line}: {message}'
        super().__init__(msg)


Rules = Mapping[str, Regex]


class SyntaxDef(object):
    def __init__(self, identifiers: List[str], rules: Rules, builder: AstBuilder):
        self._identifiers = identifiers
        self._rules = rules
        self._builder = builder

    @property
    def identifiers(self) -> List[str]:
        return self._identifiers

    @property
    def rules(self):
        return self._rules

    def parse(self, code: str, rule: Regex) -> Optional[Node]:
        rule(code)
        return self._builder.build()

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


class SyntaxDefParser(object):
    def __init__(self):
        self._builder = AstBuilder()
        self._identifiers: List[str] = []
        self._rules: Dict[str, Regex] = {}
        self._refs: Set[str] = set()

    def parse(self, value: str) -> SyntaxDef:
        gen = (line.strip().split('#')[0] for line in value.split('\n'))
        gen = ((line_number, line) for line_number, line in enumerate(gen, start=1) if line)
        for line_number, line in gen:
            self._parse_line(line, line_number)
        if unresolved_refs := self._refs - set(self._identifiers):
            raise DefError(f'Unresolved references {unresolved_refs!r}.')
        return SyntaxDef(self._identifiers, self._rules, self._builder)

    def _parse_line(self, value: str, line_number: int):
        pair = value.split('=', maxsplit=1)
        if len(pair) != 2:
            raise DefError(f'<identifier>=<rule> expected but was {value!r}.', line=line_number)

        identifier = self._parse_identifier(pair[0], line_number)
        self._identifiers.append(identifier)
        self._rules[identifier] = NodeRegex(identifier, self._parse_rule(pair[1], line_number), self._builder)

    def _parse_identifier(self, value: str, line_number: int) -> str:
        identifier = value.strip()
        if not is_identifier(identifier):
            raise DefError(f'Invalid identifier {identifier!r}.', line=line_number)
        if identifier in self._rules:
            raise DefError(f'Redefinition of identifier {identifier!r}.', line=line_number)
        return identifier

    def _parse_rule(self, value: str, line_number: int) -> Regex:
        if (rule := self._parse_options(value, line_number)) is not None:
            return rule
        if (rule := self._parse_sequence(value, line_number)) is not None:
            return rule
        if (rule := self._parse_maybe(value, line_number)) is not None:
            return rule
        if (rule := self._parse_repeat(value, line_number)) is not None:
            return rule
        if (rule := self._parse_anchor(value)) is not None:
            return rule
        if (rule := self._parse_end_of_line(value)) is not None:
            return rule
        if (rule := self._parse_ref(value)) is not None:
            return rule
        raise DefError(f'Invalid identifier {value.strip()!r}.', line=line_number)

    def _parse_options(self, value: str, line_number: int) -> Optional[Regex]:
        options = split_excluding_literals(value, '|')
        if len(options) > 1:
            return self._node(FirstOf(*(self._parse_rule(option, line_number) for option in options)))
        return None

    def _parse_sequence(self, value: str, line_number: int) -> Optional[Regex]:
        sequence = split_excluding_literals(value, ',')
        if len(sequence) > 1:
            return self._node(Seq(*(self._parse_rule(element, line_number) for element in sequence)))
        return None

    def _parse_maybe(self, value: str, line_number: int) -> Optional[Regex]:
        value = value.strip()
        if value.startswith('[') and value.endswith(']'):
            return self._node(Maybe(self._parse_rule(value[1:-1], line_number)))
        return None

    def _parse_repeat(self, value: str, line_number: int) -> Optional[Regex]:
        value = value.strip()
        if value.startswith('{') and value.endswith('}'):
            return self._node(Repeat(self._parse_rule(value[1:-1], line_number)))
        return None

    def _parse_anchor(self, value: str) -> Optional[Regex]:
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            return self._node(Eq(value[1:-1]))
        return None

    def _parse_end_of_line(self, value: str) -> Optional[Regex]:
        value = value.strip()
        if value == '$':
            return self._node(Eq('\n'))
        return None

    def _parse_ref(self, value: str) -> Optional[Regex]:
        value = value.strip()
        if is_identifier(value):
            self._refs.add(value)
            return RegexRef(lambda: self._rules[value])
        return None

    def _node(self, regex: Regex):
        return NodeRegex(None, regex, self._builder)

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self)


def is_identifier(value: str) -> bool:
    from cmaj.syntax.strings import expand
    letters = set(expand('a', 'z'))
    value_without_glue = [ch for ch in value if ch != '-']
    is_letter_or_glue = all(ch.lower() in letters for ch in value_without_glue)
    all_lower = all(ch.islower() for ch in value_without_glue)
    all_upper = all(ch.isupper() for ch in value_without_glue)
    is_valid_glue = all(len(segment) > 0 for segment in value.split('-'))
    return is_letter_or_glue and is_valid_glue and (all_lower or all_upper)


def split_excluding_literals(value: str, delimiter: str) -> List[str]:
    is_literal_count_even = True
    for index, ch in enumerate(value):
        if ch == '"':
            is_literal_count_even = not is_literal_count_even
        if ch == delimiter and is_literal_count_even:
            return [value[:index]] + split_excluding_literals(value[index + 1:], delimiter)
    return [value]
