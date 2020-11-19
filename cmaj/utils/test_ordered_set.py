from unittest import TestCase

from cmaj.utils.ordered_set import OrderedSet


class SizeTest(TestCase):
    def test_given_no_values_then_empty_set(self) -> None:
        s = OrderedSet()
        self.assertEqual(0, len(s))

    def test_given_values2134_then_size4(self) -> None:
        s = OrderedSet('2', '1', '3', '4')
        self.assertEqual(4, len(s))

    def test_given_values2123_then_size3(self) -> None:
        s = OrderedSet('2', '1', '2', '3')
        self.assertEqual(3, len(s))


class ValuesTest(TestCase):
    def test_given_no_values_then_empty_set(self) -> None:
        s = OrderedSet()
        self.assertEqual([], list(s))

    def test_given_values3132_then_set312(self) -> None:
        s = OrderedSet('3', '1', '3', '2')
        self.assertEqual(['3', '1', '2'], list(s))


class UnionTest(TestCase):
    def test_given_set123_and_values34311_then_set1234(self) -> None:
        s = OrderedSet('1', '2', '3') | ('3', '4', '3', '1', '1')
        self.assertEqual(['1', '2', '3', '4'], list(s))

    def test_given_values33441_and_set123_then_set3412(self) -> None:
        s = ('3', '3', '4', '4', '1') | OrderedSet('1', '2', '3')
        self.assertEqual(['3', '4', '1', '2'], list(s))

    def test_given_set134_and_set201_then_set13420(self) -> None:
        s = OrderedSet('1', '3', '4') | OrderedSet('2', '0', '1')
        self.assertEqual(['1', '3', '4', '2', '0'], list(s))


class EqualTest(TestCase):
    def test_given_empty_sets_then_equal(self) -> None:
        self.assertEqual(OrderedSet(), OrderedSet())

    def test_given_values1323_and_set1312_then_equal(self) -> None:
        self.assertEqual(OrderedSet('1', '3', '2', '3'), OrderedSet('1', '3', '1', '2'))

    def test_given_set123_and_set213_then_not_equal(self) -> None:
        self.assertNotEqual(OrderedSet('1', '2', '3'), OrderedSet('2', '1', '3'))

    def test_given_set12_and_set123_then_not_equal(self) -> None:
        self.assertNotEqual(OrderedSet('1', '2'), OrderedSet('1', '2', '3'))

    def test_given_equal_sets_then_same_hash(self) -> None:
        x = OrderedSet('4', '2') | ('2', '3')
        y = ('4', '2') | OrderedSet('4', '3')
        self.assertEqual(hash(x), hash(y))


class GetItemTest(TestCase):
    def test_given_set123_then_get_correct_item_by_index(self) -> None:
        s = OrderedSet('1', '2', '3')
        self.assertEqual('1', s[0])
        self.assertEqual('2', s[1])
        self.assertEqual('3', s[2])

    def test_given_set1234_then_correct_slices(self) -> None:
        s = OrderedSet('1', '2', '3', '4')
        self.assertEqual(OrderedSet(), s[:0])
        self.assertEqual(OrderedSet('1', '2', '3'), s[:3])
        self.assertEqual(OrderedSet('2', '3', '4'), s[1:])
        self.assertEqual(OrderedSet('1', '2'), s[:2])
        self.assertEqual(OrderedSet('2', '3'), s[1:3])
        self.assertEqual(OrderedSet('3', '4'), s[2:])
