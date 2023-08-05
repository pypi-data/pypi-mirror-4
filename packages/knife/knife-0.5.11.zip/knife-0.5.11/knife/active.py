# -*- coding: utf-8 -*-
'''Actively evaluated knives.'''

from threading import local
from collections import deque
from contextlib import contextmanager

from stuf.deep import clsname
from stuf.utils import loads, optimize, moptimize

from knife.base import KnifeMixin, SLOTS
from knife.mixins import (
    RepeatMixin, MapMixin, SliceMixin, ReduceMixin, FilterMixin, MathMixin,
    CmpMixin, OrderMixin)


class _ActiveMixin(local):

    '''active knife mixin'''

    def __init__(self, *things, **kw):
        '''
        :argument things: incoming things

        :keyword integer snapshots: snapshots to keep (default: ``5``)
        '''
        incoming = deque()
        incoming.extend(things)
        super(_ActiveMixin, self).__init__(incoming, deque(), **kw)
        # working things
        self._work = deque()
        # holding things
        self._hold = deque()

    def __repr__(self):
        '''String representation.'''
        # object representation
        return self._REPR(
            self.__module__,
            clsname(self),
            list(self._in),
            list(self._work),
            list(self._hold),
            list(self._out),
        )

    def __len__(self):
        '''Number of incoming things.'''
        # length of incoming things
        return len(self._in)

    def __iter__(self):
        '''Iterate over outgoing things.'''
        return iter(self._out)

    @property
    @contextmanager
    def _chain(self, d=moptimize):
        # take snapshot
        snapshot = d(self._in)
        # rebalance incoming with outcoming
        if self._history:
            self._in.clear()
            self._in.extend(self._out)
        # make snapshot original snapshot?
        else:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # move incoming things to working things
        self._work.extend(self._in)
        yield
        # clear outgoing things
        self._out.clear()
        # extend outgoing things with holding things
        self._out.extend(self._hold)
        # clear working things
        self._work.clear()
        # clear holding things
        self._hold.clear()

    @property
    def _iterable(self):
        # derived from Raymond Hettinger Python Cookbook recipe # 577155
        call = self._work.popleft
        try:
            while 1:
                yield call()
        except IndexError:
            pass

    def _append(self, thing):
        # append thing after other holding things
        self._hold.append(thing)
        return self

    def _xtend(self, things):
        # place things after holding things
        self._hold.extend(things)
        return self

    def prepend(self, *things):
        '''
        Insert `things` **before** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> __(3, 4, 5).prepend(1, 2, 3, 4, 5, 6).peek()
        [1, 2, 3, 4, 5, 6, 3, 4, 5]
        '''
        # take snapshot
        snapshot = moptimize(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place thing before other holding things
        self._in.extendleft(reversed(things))
        return self

    def append(self, *things):
        '''
        Insert `things` **after** other incoming things.

        :argument things: incoming things

        :rtype: :mod:`knife` :term:`object`

        >>> from knife import __
        >>> __(3, 4, 5).append(1, 2, 3, 4, 5, 6).peek()
        [3, 4, 5, 1, 2, 3, 4, 5, 6]
        '''
        # take snapshot
        snapshot = moptimize(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things after other incoming things
        self._in.extend(things)
        return self

    def pipe(self, knife):
        '''
        Pipe incoming things from some other :mod:`knife` :term:`object`
        through this :mod:`knife` :term:`object`.

        :argument knife: another :mod:`knife` :term:`object`

        :rtype: :mod:`knife` :term:`object`
        '''
        with self._chain:
            knife.clear()
            knife._history.clear()
            knife._history.extend(self._history)
            knife._original = self._original
            knife._baseline = self._baseline
            knife._out.extend(self._out)
            knife._worker = self._worker
            knife._args = self._args
            knife._kw = self._kw
            knife._wrapper = self._wrapper
            knife._pipe = self
            return knife

    def back(self):
        '''
        Switch back to :mod:`knife` :term:`object` that piped its incoming
        things through this :mod:`knife` :term:`object`.

        :rtype: :mod:`knife` :term:`object`
        '''
        with self._chain:
            piped = self._pipe
            piped.clear()
            piped._history.clear()
            piped._history.extend(self._history)
            piped._original = self._original
            piped._baseline = self._baseline
            piped._out.extend(self._out)
            piped._worker = self._worker
            piped._args = self._args
            piped._kw = self._kw
            piped._wrapper = self._wrapper
            self.clear()
            return piped

    def undo(self, snapshot=0):
        '''
        Revert incoming things to a previous snapshot.

        .. note::

          A snapshot of current incoming things is taken when a :mod:`knife`
          :term:`method` is called but before the main body of the method
          executes.

        :keyword int snapshot: number of steps ago ``1``, ``2``, ``3``, etc.

        :rtype: :mod:`knife` :term:`object`

        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> # undo back one step
        >>> undone.append(1).undo().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> # undo back one step
        >>> undone.append(1).append(2).undo().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1]
        >>> # undo back 2 steps
        >>> undone.append(1).append(2).undo(2).peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1]
        '''
        # clear everything
        self.clear()
        # if specified, use a specific snapshot
        if snapshot:
            self._history.rotate(-(snapshot - 1))
        try:
            this = loads(self._history.popleft())
            self._in.extend(this)
            self._out.extend(this)
        except IndexError:
            raise IndexError('nothing to undo')
        return self

    def snapshot(self):
        '''
        Take a baseline snapshot of current incoming things.

        :rtype: :mod:`knife` :term:`object`
        '''
        # take baseline snapshot of incoming things
        self._baseline = optimize(self._in)
        return self

    def baseline(self):
        '''
        Restore incoming things back to the baseline :meth:`snapshot`.

        :rtype: :mod:`knife` :term:`object`

        >>> from knife import __
        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> undone.snapshot().append(1).append(2).peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3, 1, 2]
        >>> undone.baseline().peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        '''
        # clear everything
        self.clear()
        # clear snapshots
        self._history.clear()
        # revert to baseline snapshot of incoming things
        self._in.extend(loads(self._baseline))
        return self

    def original(self):
        '''
        Restore incoming things back to the original snapshot.

        .. note::

          THe original snapshot of incoming things is taken following the first
          :mod:`knife` :term:`method` call but before the second :mod:`knife`
          :term:`method` call (if there is a second :term:`method` call)

        :rtype: :mod:`knife` :term:`object`

        >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
        >>> undone.peek()
        [1, 2, 3, 4, 5, 6, 1, 2, 3]
        >>> undone.original().peek()
        [1, 2, 3]
        '''
        # clear everything
        self.clear()
        # clear snapshots
        self._history.clear()
        # clear baseline
        self._baseline = None
        # restore original snapshot of incoming things
        self._in.extend(loads(self._original))
        return self

    def clear(self):
        '''
        Clear everything.

        :rtype: :mod:`knife` :term:`object`
        '''
        # clear worker
        self._worker = None
        # clear worker positional arguments
        self._args = ()
        # clear worker keyword arguments
        self._kw = {}
        # default iterable wrapper
        self._wrapper = list
        # clear pipe
        self._pipe = None
        # clear incoming things
        self._in.clear()
        # clear working things
        self._work.clear()
        # clear holding things
        self._hold.clear()
        # clear outgoing things
        self._out.clear()
        return self

    def peek(self):
        '''
        Preview current incoming things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one thing is returned. With
          multiple outgoing things, everything is returned wrapped with the
          wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`).
        '''
        wrap, out = self._wrapper, self._in
        value = list(wrap(i) for i in out) if self._each else wrap(out)
        self._each = False
        self._wrapper = list
        return value[0] if len(value) == 1 else value

    def get(self):
        '''
        Return outgoing things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one outgoing thing is
          returned. With multiple outgoing things, they are returned wrapped
          with the wrapper assigned with :meth:`wrap` (default wrapper is
          :func:`list`).
        '''
        wrap, out = self._wrapper, self._out
        value = list(wrap(i) for i in out) if self._each else wrap(out)
        self._each = False
        self._wrapper = list
        return value[0] if len(value) == 1 else value


class activeknife(
    _ActiveMixin, KnifeMixin, FilterMixin, MapMixin, ReduceMixin,
    OrderMixin, RepeatMixin, MathMixin, SliceMixin, CmpMixin,
):

    '''
    Actively evaluated combo knife. Provides every :mod:`knife` method.

    .. note::

      Also aliased as :class:`~knife.knife` when imported from :mod:`knife`.

    >>> from knife import knife
    '''

    __slots__ = SLOTS


class cmpknife(_ActiveMixin, KnifeMixin, CmpMixin):

    '''
    Actively evaluated comparing knife. Provides comparison operations for
    incoming things.

    >>> from knife.active import cmpknife
    '''

    __slots__ = SLOTS


class filterknife(_ActiveMixin, KnifeMixin, FilterMixin):

    '''
    Actively evaluated filtering knife. Provides filtering operations for
    incoming things.

    >>> from knife.active import filterknife
    '''

    __slots__ = SLOTS


class mapknife(_ActiveMixin, KnifeMixin, MapMixin):

    '''
    Actively evaluated mapping knife. Provides `mapping <http://docs.python.org
    /library/functions.html#map>`_ operations for incoming things.

    >>> from knife.active import mapknife
    '''

    __slots__ = SLOTS


class mathknife(_ActiveMixin, KnifeMixin, MathMixin):

    '''
    Actively evaluated mathing knife. Provides numeric and statistical
    operations for incoming things.

    >>> from knife.active import mathknife
    '''

    __slots__ = SLOTS


class orderknife(_ActiveMixin, KnifeMixin, OrderMixin):

    '''
    Actively evaluated ordering knife. Provides sorting and grouping operations
    for incoming things.

    >>> from knife.active import orderknife
    '''

    __slots__ = SLOTS


class reduceknife(_ActiveMixin, KnifeMixin, ReduceMixin):

    '''
    Actively evaluated reducing knife. Provides `reducing <http://docs.python.
    org/library/functions.html#map>`_ operations for incoming things.

    >>> from knife.active import reduceknife
    '''

    __slots__ = SLOTS


class repeatknife(_ActiveMixin, KnifeMixin, RepeatMixin):

    '''
    Actively evaluated repeating knife. Provides repetition operations for
    incoming things.

    >>> from knife.active import repeatknife
    '''

    __slots__ = SLOTS


class sliceknife(_ActiveMixin, KnifeMixin, SliceMixin):

    '''
    Actively evaluated slicing knife. Provides `slicing <http://docs.python.
    org/library/functions.html#slice>`_ operations for incoming things.

    >>> from knife.active import sliceknife
    '''

    __slots__ = SLOTS
