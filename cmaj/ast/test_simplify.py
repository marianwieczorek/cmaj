from unittest import TestCase

from cmaj.ast.simplify import prune, skip, squash


class SquashTest(TestCase):
    def test_given_root_is_leaf_then_no_squash(self) -> None:
        from cmaj.testing.ast import tree
        tree_def = ('node', [])
        result = squash(tree(tree_def), 'node')
        self.assertEqual(tree(tree_def), result)

    def test_given_single_child_to_squash_when_parent_is_root_then_child_becomes_root(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [token('X', 0)]))
        result = squash(node, 'X')
        expected = tree(token('X', 0))
        self.assertEqual(expected, result)

    def test_given_many_children_to_squash_when_parent_is_root_then_no_squash(self) -> None:
        from cmaj.testing.ast import tree, token
        tree_def = ('X', [token('X', 0), token('X', 1)])
        result = squash(tree(tree_def), 'X')
        self.assertEqual(tree(tree_def), result)

    def test_given_inner_node_to_squash_then_grandchildren_become_children(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('Y', [('X', [('X', [token('Y', 0), token('Y', 1)])])]))
        result = squash(node, 'X')
        expected = tree(('Y', [('X', [token('Y', 0), token('Y', 1)])]))
        self.assertEqual(expected, result)

    def test_given_chain_then_squash_to_single_node(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('Y', [('X', [('X', [('X', [token('Y', 0)])])])]))
        result = squash(node, 'X')
        expected = tree(('Y', [('X', [token('Y', 0)])]))
        self.assertEqual(expected, result)

    def test_given_nodes_to_squash_separated_by_other_node_then_no_squash(self) -> None:
        from cmaj.testing.ast import tree, token
        tree_def = ('X', [('Y', [token('X', 0)])])
        result = squash(tree(tree_def), 'X')
        self.assertEqual(tree(tree_def), result)

    def test_given_tree_then_correct_squash(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [('X', [token('Y', 0),
                                  ('X', [token('Y', 1),
                                         token('X', 2)])]),
                           ('Y', [('X', [token('X', 3)])])]))
        result = squash(node, 'X')
        expected = tree(('X', [token('Y', 0), token('Y', 1), token('X', 2), ('Y', [token('X', 3)])]))
        self.assertEqual(expected, result)


class PruneTest(TestCase):
    def test_given_root_is_leaf_then_no_prune(self) -> None:
        from cmaj.testing.ast import tree
        tree_def = ('node', [])
        result = prune(tree(tree_def), 'node')
        self.assertEqual(tree(tree_def), result)

    def test_given_root_with_leaf_to_prune_then_root_becomes_leaf(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [token('X', 0)]))
        result = prune(node, 'X')
        expected = tree(('X', []))
        self.assertEqual(expected, result)

    def test_when_all_children_are_pruned_then_prune_empty_nodes(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [token('Y', 0), ('Y', [token('X', 1), token('X', 2)])]))
        result = prune(node, 'X')
        expected = tree(('X', [token('Y', 0)]))
        self.assertEqual(expected, result)

    def test_given_tree_then_correct_prune(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [('X', [token('Y', 0), ('X', [token('Y', 1), token('Y', 2)])]),
                           ('Y', [('X', [token('X', 3)])])]))
        result = prune(node, 'Y')
        expected = tree(('X', []))
        self.assertEqual(expected, result)


class SkipTest(TestCase):
    def test_given_root_is_leaf_then_not_skipped(self) -> None:
        from cmaj.testing.ast import tree
        tree_def = ('node', [])
        result = skip(tree(tree_def), 'node')
        self.assertEqual(tree(tree_def), result)

    def test_given_single_child_then_child_becomes_root(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [token('X', 0)]))
        result = skip(node, 'X')
        expected = tree(token('X', 0))
        self.assertEqual(expected, result)

    def test_given_many_children_then_not_skipped(self) -> None:
        from cmaj.testing.ast import tree, token
        tree_def = ('X', [token('X', 0), token('X', 1)])
        result = skip(tree(tree_def), 'X')
        self.assertEqual(tree(tree_def), result)

    def test_given_inner_nodes_to_skip_then_leaves_become_children(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('Y', [('X', [('X', [token('Y', 0), token('Y', 1)])])]))
        result = skip(node, 'X')
        expected = tree(('Y', [token('Y', 0), token('Y', 1)]))
        self.assertEqual(expected, result)

    def test_given_inner_nodes_not_to_skip_then_not_skipped(self) -> None:
        from cmaj.testing.ast import tree, token
        tree_def = ('X', [('Y', [token('X', 0)])])
        result = skip(tree(tree_def), 'X')
        self.assertEqual(tree(tree_def), result)

    def test_given_tree_then_correct_skipping(self) -> None:
        from cmaj.testing.ast import tree, token
        node = tree(('X', [('X', [token('Y', 0),
                                  ('X', [token('Y', 1),
                                         token('X', 2)])]),
                           ('Y', [('X', [token('X', 3)])])]))
        result = skip(node, 'X')
        expected = tree(('X', [token('Y', 0), token('Y', 1), token('X', 2), ('Y', [token('X', 3)])]))
        self.assertEqual(expected, result)
