# -*- coding: utf-8 -*-
'''ordering test mixins'''

import platform

PYPY = platform.python_implementation() == 'PyPy'

class stooges: #@IgnorePep8
    name = 'moe'
    age = 40
class stoog2: #@IgnorePep8
    name = 'larry'
    age = 50
class stoog3: #@IgnorePep8
    name = 'curly'
    age = 60
    class stoog4: #@IgnorePep8
        name = 'beastly'
        age = 969


class stooge: #@IgnorePep8
    name = 'moe'
    age = 40
class stooge2(stooge): #@IgnorePep8
    pname = 'larry'
    page = 50
class stooge3(stoog2): #@IgnorePep8
    aname = 'curly'
    rage = 60
    class stooge4(stooge): #@IgnorePep8
        kname = 'beastly'
        mage = 969


class MathMixin(object):

    def test_pipe(self):
        one = self.mclass(10, 5, 100, 2, 1000)
        two = self.pipe()
        test = one.minmax().pipe(two).merge().back().min().get()
        self.assertEqual(test, 2, test)
        test = one.original().minmax().pipe(two).merge().back().max().get()
        self.assertEqual(test, 1000, test)
        test = one.original().minmax().pipe(two).merge().back().sum().get()
        self.assertEqual(test, 1002, test)

    def test_average(self):
        self.assertEqual(
            self.mclass(10, 40, 45).average().get(), 31.666666666666668,
        )

    def test_count(self):
        common = self.mclass(11, 3, 5, 11, 7, 3, 11).count().get()
        self.assertEqual(common.overall, [(11, 3), (3, 2), (5, 1), (7, 1)])
        # most common
        self.assertEqual(common.most, 11)
        # least common
        self.assertEqual(common.least, 7)

    def test_max(self):
        from stuf import stuf
        stooge = [
            stuf(name='moe', age=40),
            stuf(name='larry', age=50),
            stuf(name='curly', age=60),
        ]
        self.assertEqual(self.mclass(1, 2, 4).max().get(), 4)
        self.assertEqual(
            stuf(self.mclass(*stooge).worker(lambda x: x.age).max().get()),
            stuf(name='curly', age=60),
        )

    def test_median(self):
        self.assertEqual(self.mclass(4, 5, 7, 2, 1).median().get(), 4)
        self.assertEqual(self.mclass(4, 5, 7, 2, 1, 8).median().get(), 4.5)

    def test_min(self):
        self.assertEqual(self.mclass(10, 5, 100, 2, 1000).min().get(), 2)
        self.assertEqual(
            self.mclass(10, 5, 100, 2, 1000).worker(
            lambda x: x % 100 == 0
            ).min().get(),
            10,
        )

    def test_minmax(self):
        self.assertEqual(self.mclass(1, 2, 4).minmax().get(), (1, 4))
        self.assertEqual(
            self.mclass(10, 5, 100, 2, 1000).minmax().get(), (2, 1000),
        )

    def test_range(self):
        self.assertEqual(self.mclass(3, 5, 7, 3, 11).range().get(), 8)

    def test_sum(self):
        self.assertEqual(self.mclass(1, 2, 3).sum().get(), 6)
        self.assertEqual(self.mclass(1, 2, 3).sum(1).get(), 7)
        self.assertEqual(
            self.mclass(
                .1, .1, .1, .1, .1, .1, .1, .1, .1, .1
            ).sum(precision=True).get(),
            1.0,
        )


class CmpMixin(object):

    def test_all(self):
        from operator import truth
        self.assertFalse(
            self.mclass(True, 1, None, 'yes').worker(truth).all().get()
        )
        self.assertTrue(
            self.mclass(2, 4, 6, 8).worker(lambda x: x % 2 == 0).all().get()
        )

    def test_any(self):
        self.assertTrue(
            self.mclass(None, 0, 'yes', False).worker(bool).any().get()
        )
        self.assertTrue(
            self.mclass(1, 4, 5, 9).worker(lambda x: x % 2 == 0).any().get()
        )

    def test_difference(self):
        self.assertEqual(
            self.mclass(
                [1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2]
            ).difference().get(),
            [1, 3, 4],
        )
        self.assertEqual(
            self.mclass(
                [1, 3, 4, 5], [5, 2, 10], [10, 11, 2]
            ).difference(True).get(),
            [3, 1, 11, 4] if PYPY else [1, 3, 4, 11]
        )

    def test_intersection(self):
        self.assertEqual(
            self.mclass(
                [1, 2, 3], [101, 2, 1, 10], [2, 1]
            ).intersection().get(), [1, 2],
        )

    def test_union(self):
        self.assertEqual(
            self.mclass([1, 2, 3], [101, 2, 1, 10], [2, 1]).union().get(),
            [10, 1, 2, 3, 101] if PYPY else [1, 10, 3, 2, 101],
        )

    def test_unique(self):
        self.assertEqual(
            self.mclass(1, 2, 1, 3, 1, 4).unique().get(), [1, 2, 3, 4],
        )
        self.assertEqual(
            self.mclass(1, 2, 1, 3, 1, 4).worker(round).unique().get(),
            [1, 2, 3, 4],
        )


class OrderMixin(object):

    def test_shuffle(self):
        self.assertEqual(
            len(self.mclass(1, 2, 3, 4, 5, 6).shuffle()),
            len([5, 4, 6, 3, 1, 2]),
        )

    def test_group(self,):
        self.assertEqual(
            self.mclass(1.3, 2.1, 2.4).group().get(),
            [(1.3, (1.3,)), (2.1, (2.1,)), (2.4, (2.4,))],
        )
        from math import floor
        self.assertEqual(
            self.mclass(1.3, 2.1, 2.4).worker(floor).group().get(),
            [(1.0, (1.3,)), (2.0, (2.1, 2.4))]
        )

    def test_combo(self):
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).reverse().sort().get(), [1, 2, 3, 4, 5]
        )

    def test_reverse(self):
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).reverse().get(), [1, 2, 3, 4, 5],
        )

    def test_sort(self):
        from math import sin
        self.assertEqual(
            self.mclass(1, 2, 3, 4, 5, 6).worker(sin).sort().get(),
            [5, 4, 6, 3, 1, 2],
        )
        self.assertEqual(
            self.mclass(4, 6, 65, 3, 63, 2, 4).sort().get(),
            [2, 3, 4, 4, 6, 63, 65],
        )


class FilterMixin(object):

    def test_pattern(self):
        test = self.mclass(
            'This is the first test',
            'This is the second test',
            'This is the third test',
        ).pattern('{} first {}')
        self.assertEqual(
            test.filter().get(), 'This is the first test'
        )
        self.assertEqual(
            test.original().pattern(
                '. third .', type='regex'
            ).filter().get(), 'This is the third test'
        )
        self.assertEqual(
            test.original().pattern(
                '* second *', type='glob'
            ).filter().get(), 'This is the second test'
        )

    def test_traverse(self):
        self.maxDiff = None
        from stuf.collects import ChainMap, OrderedDict
        get = self.mclass(stoog3).traverse().get()
        self.assertEqual(
            get,
            ChainMap(OrderedDict([
                ('classname', 'stoog3'), ('age', 60), ('name', 'curly')]),
                OrderedDict([
                ('age', 969), ('name', 'beastly'), ('classname', 'stoog4')]))
        )
        def test(x): #@IgnorePep8
            if x[0] == 'name':
                return True
            elif x[0].startswith('__'):
                return True
            return False
        self.assertEqual(
            self.mclass(
                stooges, stoog2, stoog3
            ).worker(test).traverse(True).get(),
            [ChainMap(OrderedDict([('classname', 'stooges'), ('age', 40)])),
            ChainMap(OrderedDict([('classname', 'stoog2'), ('age', 50)])),
            ChainMap(
                OrderedDict([('classname', 'stoog3'), ('age', 60)]),
                OrderedDict([('classname', 'stoog4'), ('age', 969)])
            )],
        )
        get = self.mclass(stooge, stooge2, stooge3).traverse().get()
        self.assertEqual(
            get,
            [ChainMap(OrderedDict([
                ('classname', 'stooge'), ('age', 40), ('name', 'moe')])),
            ChainMap(
                OrderedDict([
                    ('classname', 'stooge'), ('age', 40), ('name', 'moe'),
                    ('classname', 'stooge2'), ('page', 50), ('pname', 'larry')
                ])
            ),
            ChainMap(OrderedDict([
                ('classname', 'stooge3'), ('age', 50), ('aname', 'curly'),
                ('name', 'larry'), ('rage', 60)]), OrderedDict([('age', 40),
                ('kname', 'beastly'), ('mage', 969), ('name', 'moe'),
                ('classname', 'stooge4')]))
    ])

    def test_attrs(self):
        from stuf import stuf
        stooge = [
            stuf(name='moe', age=40),
            stuf(name='larry', age=50),
            stuf(name='curly', age=60)
        ]
        self.assertEqual(
            self.mclass(*stooge).attrs('name').get(),
            ['moe', 'larry', 'curly'],
        )
        self.assertEqual(
            self.mclass(*stooge).attrs('name', 'age').get(),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        self.assertEqual(
            self.mclass(*stooge).attrs('place').get(), [],
        )

    def test_items(self):
        from stuf import stuf
        stooge = [
            stuf(name='moe', age=40),
            stuf(name='larry', age=50),
            stuf(name='curly', age=60)
        ]
        self.assertEqual(
            self.mclass(*stooge).items('name').get(),
            ['moe', 'larry', 'curly'],
        )
        self.assertEqual(
            self.mclass(*stooge).items('name', 'age').get(),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
        self.assertEqual(
            self.mclass(*stooge).items(0).get(), ['moe', 'larry', 'curly'],
        )
        self.assertEqual(self.mclass(*stooge).items(1).get(), [40, 50, 60])
        self.assertEqual(self.mclass(*stooge).items('place').get(), [])

    def test_filter(self):
        self.assertEqual(
            self.mclass(1, 2, 3, 4, 5, 6).worker(
                lambda x: x % 2 == 0
            ).filter(invert=True).get(), [1, 3, 5]
        )
        self.assertEqual(
            self.mclass(1, 2, 3, 4, 5, 6).worker(
                lambda x: x % 2 == 0
            ).filter().get(), [2, 4, 6]
        )

    def test_duality(self):
        self.assertEqual(
            self.mclass(1, 2, 3, 4, 5, 6).worker(
                lambda x: x % 2 == 0
            ).duality().get(),
            ((2, 4, 6), (1, 3, 5))
        )

    def test_members(self):
        self.assertEqual(
            self.mclass(stoog3).members().get(),
            [('age', 60), ('name', 'curly'), ('stoog4', stoog3.stoog4)],
        )
        results = self.mclass(stoog3).members(True).get()
        self.assertIn(('__doc__', None), results)
        self.assertIn(('__module__', 'tests.mixins'), results)

    def test_mro(self):
        results = self.mclass(stooge3).mro().get()
        self.assertIn(stooge3, results)
        self.assertIn(stoog2, results)


class SliceMixin(object):

    def test_dice(self):
        self.assertEqual(
            self.mclass(
                'moe', 'larry', 'curly', 30, 40, 50, True
            ).dice(2, 'x').get(),
            [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
        )

    def test_first(self):
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).first().get(), 5)
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).first(2).get(), [5, 4])

    def test_combo(self):
        self.assertEqual(self.mclass(
            5, 4, 3, 2, 1).initial().rest().slice(1, 2).last().get(), 3,
        )

    def test_index(self):
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).at(2).get(), 3)
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).at(10, 11).get(), 11)

    def test_slice(self):
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).slice(2).get(), [5, 4])
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).slice(2, 4).get(), [3, 2]
        )
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).slice(2, 4, 2).get(), 3
        )

    def test_last(self):
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).last().get(), 1)
        self.assertEqual(self.mclass(5, 4, 3, 2, 1).last(2).get(), [2, 1])

    def test_initial(self):
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).initial().get(), [5, 4, 3, 2]
        )

    def test_rest(self):
        self.assertEqual(
            self.mclass(5, 4, 3, 2, 1).rest().get(), [4, 3, 2, 1],
        )

    def test_choice(self):
        self.assertEqual(
            len(list(self.mclass(1, 2, 3, 4, 5, 6).choice())), 1,
        )

    def test_sample(self):
        self.assertEqual(
            len(self.mclass(1, 2, 3, 4, 5, 6).sample(3).get()), 3,
        )


class ReduceMixin(object):

    def test_flatten(self):
        self.assertEqual(
            self.mclass([[1, [2], [3, [[4]]]], 'here']).flatten().get(),
            [1, 2, 3, 4, 'here'],
        )

    def test_merge(self):
        self.assertEqual(
            self.mclass(
                ['moe', 'larry', 'curly'], [30, 40, 50], [True, False, False]
            ).merge().get(),
            ['moe', 'larry', 'curly', 30, 40, 50, True, False, False],
        )

    def test_reduce(self):
        self.assertEqual(
            self.mclass(1, 2, 3).worker(lambda x, y: x + y).reduce().get(),
            6,
        )
        self.assertEqual(
            self.mclass(1, 2, 3).worker(lambda x, y: x + y).reduce(1).get(),
            7,
        )
        self.assertEqual(
            self.mclass([0, 1], [2, 3], [4, 5]).worker(
                lambda x, y: x + y
            ).reduce(reverse=True).get(), [4, 5, 2, 3, 0, 1],
        )
        self.assertEqual(
            self.mclass([0, 1], [2, 3], [4, 5]).worker(
                lambda x, y: x + y
            ).reduce([0, 0], True).get(), [4, 5, 2, 3, 0, 1, 0, 0],
        )

    def test_zip(self):
        self.assertEqual(
            self.mclass(
                ['moe', 'larry', 'curly'], [30, 40, 50], [True, False, False]
            ).zip().get(),
            [('moe', 30, True), ('larry', 40, False), ('curly', 50, False)],
        )


class RepeatMixin(object):

    def test_repeat(self):
        def test(*args): #@IgnorePep8
            return list(args)
        self.assertEqual(
            self.mclass(40, 50, 60).repeat(3).get(),
            [(40, 50, 60), (40, 50, 60), (40, 50, 60)],
        )
        self.assertEqual(
            self.mclass(40, 50, 60).worker(test).repeat(3, True).get(),
            [[40, 50, 60], [40, 50, 60], [40, 50, 60]],
        )

    def test_copy(self):
        testlist = [[1, [2, 3]], [4, [5, 6]]]
        newlist = self.mclass(testlist).copy().get()
        self.assertFalse(newlist is testlist)
        self.assertListEqual(newlist, testlist)
        self.assertFalse(newlist[0] is testlist[0])
        self.assertListEqual(newlist[0], testlist[0])
        self.assertFalse(newlist[1] is testlist[1])
        self.assertListEqual(newlist[1], testlist[1])

    def test_permutations(self):
        self.assertEqual(
            self.mclass(40, 50, 60).permutate(2).get(),
            [(40, 50), (40, 60), (50, 40), (50, 60), (60, 40), (60, 50)],
        )

    def test_combination(self):
        self.assertEqual(
            self.mclass(40, 50, 60).combinate(2).get(),
            [(40, 50), (40, 60), (50, 60)],
        )


class MapMixin(object):

    def test_factory(self):
        from stuf import stuf
        thing = self.mclass(
            [('a', 1), ('b', 2), ('c', 3)], [('a', 1), ('b', 2), ('c', 3)]
        ).worker(stuf).map().get()
        self.assertEqual(
            thing, [stuf(a=1, b=2, c=3), stuf(a=1, b=2, c=3)]
        )

    def test_kwargmap(self):
        def test(*args, **kw):
            return sum(args) * sum(kw.values())
        self.assertEqual(
            self.mclass(
                ((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})
            ).worker(test).kwargmap().get(),
            [6, 10, 14],
        )
        self.assertEqual(
            self.mclass(
                ((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})
            ).worker(test).params(
                1, 2, 3, b=5, w=10, y=13
            ).kwargmap(True).get(),
            [270, 330, 390],
        )
        self.assertEqual(
            self.mclass(
                ((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})
            ).apply(
                test, 1, 2, 3, b=5, w=10, y=13
            ).kwargmap(True).get(),
            [270, 330, 390],
        )

    def test_argmap(self):
        self.assertEqual(
            self.mclass(
                (1, 2), (2, 3), (3, 4)
            ).worker(lambda x, y: x * y).argmap().get(),
            [2, 6, 12],
        )
        self.assertEqual(
            self.mclass((1, 2), (2, 3), (3, 4)).worker(
                lambda x, y, z, a, b: x * y * z * a * b
            ).params(7, 8, 9).argmap(True).get(),
            [1008, 3024, 6048],
        )
        self.assertEqual(
            self.mclass((1, 2), (2, 3), (3, 4)).apply(
                lambda x, y, z, a, b: x * y * z * a * b, 7, 8, 9
            ).argmap(True).get(),
            [1008, 3024, 6048],
        )

    def test_map(self):
        self.assertEqual(
            self.mclass(1, 2, 3).worker(lambda x: x * 3).map().get(),
            [3, 6, 9],
        )

    def test_invoke(self):
        self.assertEqual(
            self.mclass(
                [5, 1, 7], [3, 2, 1]
            ).params(1).invoke('index').get(),
            [1, 2],
        )
        self.assertEqual(
            self.mclass([5, 1, 7], [3, 2, 1]).invoke('sort').get(),
            [[1, 5, 7], [1, 2, 3]],
        )

    def test_mapping(self):
        self.assertEqual(
            self.mclass(
                dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
            ).mapping(True).get(), [1, 2, 3, 1, 2, 3],
        )
        self.assertEqual(
            self.mclass(
                dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
            ).mapping(values=True).get(),
            [2, 3, 4, 2, 3, 4],
        )
        self.assertEqual(
            self.mclass(
                dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
            ).worker(lambda x, y: x * y).mapping().get(),
            [2, 6, 12, 2, 6, 12],
        )
        self.assertEqual(
            self.mclass(
                dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
            ).mapping().wrap(dict).get(),
            dict([(1, 2), (2, 3), (3, 4)]),
        )


class Mixin(object):

    def test_repr(self):
        from stuf.six import strings
        self.assertIsInstance(
            self.mclass([1, 2, 3, 4, 5, 6]).__repr__(), strings,
        )

    def test_append(self):
        self.assertEqual(self.mclass().append('foo').peek(), 'foo')
        self.assertListEqual(
            self.mclass().append(1, 2, 3, 4, 5, 6).peek(),
            [1, 2, 3, 4, 5, 6],
        )

    def test_prepend(self):
        self.assertEqual(self.mclass().prepend('foo').peek(), 'foo')
        self.assertListEqual(
            self.mclass().prepend(1, 2, 3, 4, 5, 6).peek(), [1, 2, 3, 4, 5, 6]
        )

    def test_undo(self):
        queue = self.mclass(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        self.assertEqual(queue.peek(), [1, 2, 3, 4, 5, 6, 1, 2, 3])
        queue.append(1).undo()
        self.assertEqual(queue.peek(), [1, 2, 3, 4, 5, 6, 1, 2, 3])
        queue.append(1).append(2).undo()
        self.assertEqual(queue.peek(), [1, 2, 3, 4, 5, 6, 1, 2, 3, 1])
        queue.append(1).append(2).undo(2)
        self.assertEqual(queue.peek(), [1, 2, 3, 4, 5, 6, 1, 2, 3, 1])
        queue.snapshot().append(1).append(2).baseline()
        self.assertEqual(queue.peek(), [1, 2, 3, 4, 5, 6, 1, 2, 3, 1])
        queue.original()
        self.assertEqual(queue.peek(), [1, 2, 3])
        self.assertRaises(IndexError, lambda: queue.undo().undo())

    def test_wrap(self):
        self.assertIsInstance(
            self.mclass(1, 2, 3, 4, 5, 6).wrap(tuple).peek(), tuple,
        )
        self.assertTupleEqual(
            self.mclass(1, 2, 3, 4, 5, 6).wrap(tuple).peek(),
            (1, 2, 3, 4, 5, 6),
        )

    def test_ascii(self):
        from stuf.six import u, b
        self.assertEqual(
            self.mclass(
                [1], True, r't', b('i'), u('g'), None, (1,)
            ).ascii().oneach().peek(),
            [b('[1]'), b('True'), b('t'), b('i'), b('g'), b('None'), b('(1,)')]
        )

    def test_bytes(self):
        from stuf.six import u, b
        self.assertEqual(
            self.mclass(
                [1], True, r't', b('i'), u('g'), None, (1,)
            ).bytes().oneach().peek(),
            [b('[1]'), b('True'), b('t'), b('i'), b('g'), b('None'), b('(1,)')]
        )

    def test_unicode(self):
        from stuf.six import u, b
        self.assertEqual(
            self.mclass(
                [1], True, r't', b('i'), u('g'), None, (1,)
            ).unicode().oneach().peek(),
            [u('[1]'), u('True'), u('t'), u('i'), u('g'), u('None'), u('(1,)')]
        )
