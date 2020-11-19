from typing import AbstractSet, Any, Mapping, Optional


def stringify(self_: Any, use: Optional[Mapping[str, Any]] = None, hide: Optional[AbstractSet[str]] = None) -> str:
    name = self_.__class__.__name__
    state = self_.__dict__
    return f'{name}({_stringify_state(state, use or {}, hide or set())})'


def _stringify_state(current_state: Mapping[str, Any],
                     custom_field_repr: Mapping[str, Any],
                     hidden_fields: AbstractSet[str]) -> str:
    hidden_fields = {_strip_qualifiers(field) for field in hidden_fields}
    current_state = {_strip_qualifiers(key): value for key, value in current_state.items()}
    custom_field_repr = {_strip_qualifiers(key): value for key, value in custom_field_repr.items()}
    current_state.update(custom_field_repr)
    return ', '.join(f'{key}: {value!r}' for key, value in current_state.items() if key not in hidden_fields)


def _strip_qualifiers(value: str) -> str:
    return value.lstrip('_')
