# -*- coding: utf-8 -*-
'''lazy knife tests'''

from stuf.six import unittest

from tests.mixins import (
    Mixin, MapMixin, RepeatMixin, ReduceMixin, SliceMixin, FilterMixin,
    OrderMixin, MathMixin, CmpMixin)


class TestLazy(
    unittest.TestCase, Mixin, CmpMixin, MapMixin, ReduceMixin, OrderMixin,
    SliceMixin, RepeatMixin, MathMixin, FilterMixin,
):

    def setUp(self):
        from knife import lazyknife
        self.mclass = lazyknife
        self.pipe = lazyknife


class TestCompare(unittest.TestCase, Mixin, CmpMixin):

    def setUp(self):
        from knife.lazy import cmpknife
        self.mclass = cmpknife


class TestFilter(unittest.TestCase, Mixin, FilterMixin):

    def setUp(self):
        self.maxDiff = None
        from knife.lazy import filterknife
        self.mclass = filterknife


class TestMap(unittest.TestCase, Mixin, MapMixin):

    def setUp(self):
        from knife.lazy import mapknife
        self.mclass = mapknife


class TestMath(unittest.TestCase, Mixin, MathMixin):

    def setUp(self):
        from knife.lazy import mathknife, reduceknife
        self.mclass = mathknife
        self.pipe = reduceknife


class TestOrder(unittest.TestCase, Mixin, OrderMixin):

    def setUp(self):
        from knife.lazy import orderknife
        self.mclass = orderknife


class TestRepeat(unittest.TestCase, Mixin, RepeatMixin):

    def setUp(self):
        from knife.lazy import repeatknife
        self.mclass = repeatknife


class TestReduce(unittest.TestCase, Mixin, ReduceMixin):

    def setUp(self):
        from knife.lazy import reduceknife
        self.mclass = reduceknife


class TestSlice(unittest.TestCase, Mixin, SliceMixin):

    def setUp(self):
        from knife.lazy import sliceknife
        self.mclass = sliceknife

if __name__ == '__main__':
    unittest.main()
