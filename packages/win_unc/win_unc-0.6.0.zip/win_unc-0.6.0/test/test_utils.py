from unittest import TestCase

from win_unc.internal import utils as U


never = lambda _: False
always = lambda _: True
is_alpha = lambda x: x.isalpha()


class ListTransformerTestCase(TestCase):
    def assertEqualAsLists(self, first, second):
        self.assertEqual(list(first), list(second))


class TestDropWhile(ListTransformerTestCase):
    def test_drop_nothing(self):
        self.assertEqualAsLists(U.drop_while(never, ''), '')
        self.assertEqualAsLists(U.drop_while(never, 'a'), 'a')
        self.assertEqualAsLists(U.drop_while(never, 'abc'), 'abc')

    def test_drop_everything(self):
        self.assertEqualAsLists(U.drop_while(always, ''), '')
        self.assertEqualAsLists(U.drop_while(always, 'a'), '')
        self.assertEqualAsLists(U.drop_while(always, 'abc'), '')

    def test_drop_with_predicate(self):
        not_alpha = lambda x: not x.isalpha()
        self.assertEqualAsLists(U.drop_while(not_alpha, ''), '')
        self.assertEqualAsLists(U.drop_while(not_alpha, 'abc'), 'abc')
        self.assertEqualAsLists(U.drop_while(not_alpha, '123abc456'), 'abc456')
        self.assertEqualAsLists(U.drop_while(not_alpha, '   abc   '), 'abc   ')
        self.assertEqualAsLists(U.drop_while(not_alpha, '   '), '')


class TestTakeWhile(ListTransformerTestCase):
    def test_take_nothing(self):
        self.assertEqualAsLists(U.take_while(never, ''), '')
        self.assertEqualAsLists(U.take_while(never, 'a'), '')
        self.assertEqualAsLists(U.take_while(never, 'abc'), '')

    def test_take_everything(self):
        self.assertEqualAsLists(U.take_while(always, ''), '')
        self.assertEqualAsLists(U.take_while(always, 'a'), 'a')
        self.assertEqualAsLists(U.take_while(always, 'abc'), 'abc')

    def test_take_with_predicate(self):
        self.assertEqualAsLists(U.take_while(is_alpha, ''), '')
        self.assertEqualAsLists(U.take_while(is_alpha, 'abc'), 'abc')
        self.assertEqualAsLists(U.take_while(is_alpha, '123abc456'), '')
        self.assertEqualAsLists(U.take_while(is_alpha, '   abc   '), '')
        self.assertEqualAsLists(U.take_while(is_alpha, '   '), '')


class TestFirst(TestCase):
    def test_no_match(self):
        self.assertEqual(U.first(never, ''), None)
        self.assertEqual(U.first(never, 'abc'), None)

    def test_all_match(self):
        self.assertEqual(U.first(always, ''), None)
        self.assertEqual(U.first(always, 'abc'), 'a')

    def test_with_predicate(self):
        self.assertEqual(U.first(is_alpha, ''), None)
        self.assertEqual(U.first(is_alpha, 'abc'), 'a')
        self.assertEqual(U.first(is_alpha, '123abc'), 'a')
        self.assertEqual(U.first(is_alpha, '   abc'), 'a')


class TestReversedFirst(TestCase):
    def test_no_match(self):
        self.assertEqual(U.rfirst(never, ''), None)
        self.assertEqual(U.rfirst(never, 'abc'), None)

    def test_all_match(self):
        self.assertEqual(U.rfirst(always, ''), None)
        self.assertEqual(U.rfirst(always, 'abc'), 'c')

    def test_with_predicate(self):
        self.assertEqual(U.rfirst(is_alpha, ''), None)
        self.assertEqual(U.rfirst(is_alpha, 'abc'), 'c')
        self.assertEqual(U.rfirst(is_alpha, 'abc123'), 'c')
        self.assertEqual(U.rfirst(is_alpha, 'abc   '), 'c')


class TestHigherOrderNot(TestCase):
    def test_not_(self):
        false_ = lambda: False
        true_ = lambda: True
        id_ = lambda x: x

        self.assertEqual(U.not_(false_)(), True)
        self.assertEqual(U.not_(id_)(False), True)

        self.assertEqual(U.not_(true_)(), False)
        self.assertEqual(U.not_(id_)(True), False)


class TestRekeyDict(TestCase):
    def test_rekey_dict(self):
        self.assertEqual(U.rekey_dict({}, {}), {})
