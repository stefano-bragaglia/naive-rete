from unittest import TestCase

from assertpy import assert_that

from rete.common import Triple


class TestTriple(TestCase):

    def test__subj(self):
        for i, (subj, pred, obj, exp) in enumerate([
            ('a', 'b', 'c', 'a'),
            ('$a', 'b', 'c', '$a'),
            ('a', '$b', 'c', 'a'),
            ('a', 'b', '$c', 'a'),
            ('$a', '$b', 'c', '$a'),
            ('$a', 'b', '$c', '$a'),
            ('a', '$b', '$c', 'a'),
            ('$a', '$b', '$c', '$a'),
        ]):
            with self.subTest(i=i, subj=subj, pred=pred, obj=obj, exp=exp):
                result = Triple(subj, pred, obj).subj

                assert_that(result, 'subj').is_equal_to(exp)

    def test__pred(self):
        for i, (subj, pred, obj, exp) in enumerate([
            ('a', 'b', 'c', 'b'),
            ('$a', 'b', 'c', 'b'),
            ('a', '$b', 'c', '$b'),
            ('a', 'b', '$c', 'b'),
            ('$a', '$b', 'c', '$b'),
            ('$a', 'b', '$c', 'b'),
            ('a', '$b', '$c', '$b'),
            ('$a', '$b', '$c', '$b'),
        ]):
            with self.subTest(i=i, subj=subj, pred=pred, obj=obj, exp=exp):
                result = Triple(subj, pred, obj).pred

                assert_that(result, 'pred').is_equal_to(exp)

    def test__obj(self):
        for i, (subj, pred, obj, exp) in enumerate([
            ('a', 'b', 'c', 'c'),
            ('$a', 'b', 'c', 'c'),
            ('a', '$b', 'c', 'c'),
            ('a', 'b', '$c', '$c'),
            ('$a', '$b', 'c', 'c'),
            ('$a', 'b', '$c', '$c'),
            ('a', '$b', '$c', '$c'),
            ('$a', '$b', '$c', '$c'),
        ]):
            with self.subTest(i=i, subj=subj, pred=pred, obj=obj, exp=exp):
                result = Triple(subj, pred, obj).obj

                assert_that(result, 'obj').is_equal_to(exp)

    def test__vars(self):
        for i, (subj, pred, obj, exp) in enumerate([
            ('a', 'b', 'c', []),
            ('$a', 'b', 'c', ['$a']),
            ('a', '$b', 'c', ['$b']),
            ('a', 'b', '$c', ['$c']),
            ('$a', '$b', 'c', ['$a', '$b']),
            ('$a', 'b', '$c', ['$a', '$c']),
            ('a', '$b', '$c', ['$b', '$c']),
            ('$a', '$b', '$c', ['$a', '$b', '$c']),
        ]):
            with self.subTest(i=i, subj=subj, pred=pred, obj=obj, exp=exp):
                result = Triple(subj, pred, obj).vars

                assert_that(result, 'vars').is_equal_to(exp)

    def test__contain(self):
        for i, (subj, pred, obj, val, exp) in enumerate([
            ('$a', '$b', '$c', '$a', 'subj'),
            ('$a', '$b', '$c', '$b', 'pred'),
            ('$a', '$b', '$c', '$c', 'obj'),
            ('$a', '$b', '$c', '$d', None),
        ]):
            with self.subTest(i=i, subj=subj, pred=pred, obj=obj, val=val, exp=exp):
                result = Triple(subj, pred, obj).contain(val)

                assert_that(result, 'contain').is_equal_to(exp)


class TestHas(TestCase):

    def test__match(self):
        self.fail()


class TestWME(TestCase):

    def test_amemories(self):
        self.fail()

    def test_tokens(self):
        self.fail()

    def test_negative_join_results(self):
        self.fail()

    def test_add_memory(self):
        self.fail()

    def test_remove_memory(self):
        self.fail()

    def test_add_token(self):
        self.fail()

    def test_remove_token(self):
        self.fail()

    def test_add_negative_join_result(self):
        self.fail()

    def test_remove_negative_join_result(self):
        self.fail()
