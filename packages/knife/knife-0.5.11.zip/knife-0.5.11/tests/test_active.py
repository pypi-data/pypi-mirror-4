# -*- coding: utf-8 -*-
'''active knife tests'''

from stuf.six import unittest

from tests.mixins import (
    Mixin, MapMixin, RepeatMixin, ReduceMixin, SliceMixin, FilterMixin,
    OrderMixin, MathMixin, CmpMixin)


class TestActive(
    unittest.TestCase, Mixin, FilterMixin, MapMixin, ReduceMixin, OrderMixin,
    SliceMixin, RepeatMixin, MathMixin, CmpMixin,
):

    def setUp(self):
        from knife import activeknife
        self.mclass = activeknife
        self.pipe = activeknife


class TestCompare(unittest.TestCase, Mixin, CmpMixin):

    def setUp(self):
        from knife.active import cmpknife
        self.mclass = cmpknife


class TestFilter(unittest.TestCase, Mixin, FilterMixin):

    def setUp(self):
        self.maxDiff = None
        from knife.active import filterknife
        self.mclass = filterknife


class TestMap(unittest.TestCase, Mixin, MapMixin):

    def setUp(self):
        from knife.active import mapknife
        self.mclass = mapknife


class TestMath(unittest.TestCase, Mixin, MathMixin):

    def setUp(self):
        from knife.active import mathknife, reduceknife
        self.mclass = mathknife
        self.pipe = reduceknife


class TestOrder(unittest.TestCase, Mixin, OrderMixin):

    def setUp(self):
        from knife.active import orderknife
        self.mclass = orderknife


class TestReduce(unittest.TestCase, Mixin, ReduceMixin):

    def setUp(self):
        from knife.active import reduceknife
        self.mclass = reduceknife


class TestRepeat(unittest.TestCase, Mixin, RepeatMixin):

    def setUp(self):
        from knife.active import repeatknife
        self.mclass = repeatknife


class TestSlice(unittest.TestCase, Mixin, SliceMixin):

    def setUp(self):
        from knife.active import sliceknife
        self.mclass = sliceknife


if __name__ == '__main__':
    unittest.main()
