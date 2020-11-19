from unittest import TestCase

from cmaj.ast.node import Node, Token


class NodeEqualTest(TestCase):
    def test_given_equal_nodes_then_equal(self) -> None:
        from cmaj.testing.ast import tree
        tree_def = ('node', [('child1', Token(0, 0, 'this')),
                             ('child2', Token(0, 5, 'is')),
                             ('child3', Token(2, 4, 'awesome'))])
        node = tree(tree_def)
        other = tree(tree_def)
        self.assertEqual(other, node)

    def test_given_different_keys_then_not_equal(self) -> None:
        node = Node('node')
        other = Node('other')
        self.assertNotEqual(other, node)

    def test_given_different_tokens_then_not_equal(self) -> None:
        node = Node('node', token=Token(0, 0, 'value'))
        self.assertNotEqual(Node('node', token=Token(0, 0, 'other')), node)
        self.assertNotEqual(Node('node', token=Token(0, 1, 'value')), node)
        self.assertNotEqual(Node('node', token=Token(1, 0, 'value')), node)

    def test_given_different_number_of_children_then_not_equal(self) -> None:
        from cmaj.testing.ast import tree
        node = tree(('node', [('child1', Token(0, 0, 'value'))]))
        other = tree(('node', [('child1', Token(0, 0, 'value')), ('child2', Token(0, 0, 'value'))]))
        self.assertNotEqual(other, node)

    def test_given_different_children_then_not_equal(self) -> None:
        from cmaj.testing.ast import tree
        node = tree(('node', [('child1', Token(0, 0, 'value')), ('child2', Token(1, 0, 'value'))]))
        other = tree(('node', [('child1', Token(0, 0, 'value')), ('child2', Token(1, 0, 'other'))]))
        self.assertNotEqual(other, node)

    def test_node_is_not_hashable(self) -> None:
        node = Node('key')
        self.assertRaises(TypeError, hash, node)


class NodeLengthTest(TestCase):
    def test_given_leaf_then_length_is_zero(self) -> None:
        node = Node('node')
        self.assertEqual(0, len(node))

    def test_given_token_then_length_of_token(self) -> None:
        node = Node('node', Token(3, 2, 'value'))
        self.assertEqual(5, len(node))

    def test_given_children_then_length_of_column_span(self) -> None:
        from cmaj.testing.ast import tree
        node = tree(('node', [('child1', Token(3, 2, 'value')), ('child2', Token(3, 9, 'other'))]))
        self.assertEqual(12, len(node))

    def test_given_multiple_lines_then_length_of_last_line(self) -> None:
        from cmaj.testing.ast import tree
        node = tree(('node', [('child1', Token(3, 0, 'wrong length')), ('child2', Token(5, 2, 'correct'))]))
        self.assertEqual(7, len(node))


class NodeChildrenTest(TestCase):
    def test_new_node_is_leaf(self) -> None:
        node = Node('node')
        self.assertEqual(0, len(node.children))

    def test_when_adding_child_with_zero_length_then_error(self) -> None:
        node = Node('node', token=Token(0, 0, 'value'))
        child = Node('child')
        self.assertRaises(AssertionError, node.add_child, child)

    def test_given_node_with_token_when_adding_child_then_error(self) -> None:
        node = Node('node', token=Token(0, 0, 'value'))
        child = Node('child', token=Token(1, 0, 'value'))
        self.assertRaises(AssertionError, node.add_child, child)

    def test_when_adding_node_then_node_is_child(self) -> None:
        node = Node('node')
        child = Node('child', token=Token(0, 0, 'value'))
        node.add_child(child)
        self.assertIn(child, node.children)

    def test_children_are_copy(self) -> None:
        node = Node('node')
        child = Node('child', token=Token(0, 0, 'value'))
        node.add_child(child)

        children = node.children
        children.append(Node('no_child_of_node'))
        self.assertEqual([child], node.children)
