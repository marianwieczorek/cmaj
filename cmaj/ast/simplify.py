from cmaj.ast.node import Node


def squash(parent: Node, *keys: str) -> Node:
    for key in keys:
        parent = _squash(parent, key)
    return parent


def _squash(parent: Node, key: str) -> Node:
    new_parent = Node(parent.key, token=parent.token)
    new_children = [_squash(child, key) for child in parent.children]
    if not new_children or parent.key != key:
        new_parent.add_children(*new_children)
        return new_parent

    if (new_child := new_children[0]).key == key and len(new_children) == 1:
        return new_child

    for new_child in new_children:
        if new_child.key != key or not new_child.children:
            new_parent.add_child(new_child)
        else:
            new_parent.add_children(*new_child.children)
    return new_parent


def prune(parent: Node, *keys: str) -> Node:
    new_node = Node(parent.key, token=parent.token)
    gen = (prune(child, *keys) for child in parent.children if child.key not in keys)
    new_node.add_children(*(child for child in gen if len(child) > 0))
    return new_node


def skip(parent: Node, *keys: str) -> Node:
    new_parent = squash(parent, *keys)
    for key in keys:
        new_parent = _skip(new_parent, key)
    return new_parent


def _skip(parent: Node, key: str) -> Node:
    new_parent = Node(parent.key, token=parent.token)
    new_children = [_skip(child, key) for child in parent.children]
    for new_child in new_children:
        if new_child.key != key or not new_child.children:
            new_parent.add_child(new_child)
        else:
            new_parent.add_children(*new_child.children)
    return new_parent
