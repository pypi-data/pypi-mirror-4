# -*- coding: utf-8 -*-
'''Lazier evaluated knives.'''

from threading import local
from itertools import tee, chain
from contextlib import contextmanager

from stuf.deep import clsname
from stuf.iterable import count

from knife.base import SLOTS, KnifeMixin
from knife.mixins import (
    RepeatMixin, MapMixin, SliceMixin, ReduceMixin, FilterMixin, MathMixin,
    CmpMixin, OrderMixin)


class _LazyMixin(local):

    '''Lazy knife mixin.'''

    def __init__(self, *things, **kw):
        '''
        :argument things: incoming things
        :keyword integer snapshots: snapshots to keep (default: ``5``)
        '''
        incoming = (
            (things[0],).__iter__() if len(things) == 1 else things.__iter__()
        )
        super(_LazyMixin, self).__init__(incoming, ().__iter__(), **kw)
        # working things
        self._work = ().__iter__()
        # holding things
        self._hold = ().__iter__()

    def __repr__(self):
        '''String representation.'''
        # object representation
        self._in, in2 = tee(self._in)
        self._out, out2 = tee(self._out)
        self._work, work2 = tee(self._work)
        self._hold, hold2 = tee(self._hold)
        return self._REPR(
            self.__module__,
            clsname(self),
            list(in2),
            list(work2),
            list(hold2),
            list(out2),
        )

    def __len__(self):
        '''Number of incoming things.'''
        # length of incoming things
        self._in, incoming = tee(self._in)
        return count(incoming)

    def __iter__(self):
        '''Iterate over outgoing things.'''
        self._out, outs = tee(self._out)
        return outs

    @property
    @contextmanager
    def _chain(self, tee_=tee):
        # take snapshot
        self._in, snapshot = tee_(self._in)
        # rebalance incoming with outcoming
        if self._history:
            self._in, self._out = tee_(self._out)
        # make snapshot original snapshot?
        else:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # move incoming things to working things
        work, self._in = tee_(self._in)
        self._work = work
        yield
        # extend outgoing things with holding things
        self._out = self._hold
        # clear working things
        del self._work
        self._work = ().__iter__()
        # clear holding things
        del self._hold
        self._hold = ().__iter__()

    @property
    def _iterable(self):
        # iterable derived from link in chain
        return self._work

    def _xtend(self, things, chain_=chain):
        # place things after holding things
        self._hold = chain_(things, self._hold)
        return self

    def _append(self, things, chain_=chain):
        # append thing after other holding things
        self._hold = chain_(self._hold, (things,).__iter__())
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
        self._in, snapshot = tee(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things before other incoming things
        self._in = chain(things, self._in)
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
        self._in, snapshot = tee(self._in)
        # make snapshot original snapshot?
        if self._original is None:
            self._original = snapshot
        # place snapshot at beginning of snapshot stack
        self._history.appendleft(snapshot)
        # place things before other incoming things
        self._in = chain(self._in, things)
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
            knife._out = self._out
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
            piped._out = self._out
            piped._worker = self._worker
            piped._args = self._args
            piped._kw = self._kw
            piped._wrapper = self._wrapper
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
            self._in, self._out = tee(self._history.popleft())
        except IndexError:
            raise IndexError('nothing to undo')
        return self

    def snapshot(self):
        '''
        Take a baseline snapshot of current incoming things.

        :rtype: :mod:`knife` :term:`object`
        '''
        # take baseline snapshot of incoming things
        self._in, self._baseline = tee(self._in)
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
        self._in, self._baseline = tee(self._baseline)
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
        self._in, self._original = tee(self._original)
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
        # revert to default iterable wrapper
        self._wrapper = list
        # clear pipe
        self._pipe = None
        # clear incoming things
        del self._in
        self._in = ().__iter__()
        # clear working things
        del self._work
        self._work = ().__iter__()
        # clear holding things
        del self._hold
        self._hold = ().__iter__()
        # clear outgoing things
        del self._out
        self._out = ().__iter__()
        return self

    def peek(self):
        '''
        Preview current incoming things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one thing is returned. With
          multiple outgoing things, everything is returned wrapped with the
          wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`).
        '''
        tell, self._in, out = tee(self._in, 3)
        wrap = self._wrapper
        value = list(wrap(i) for i in out) if self._each else wrap(out)
        # reset each flag
        self._each = False
        # reset wrapper
        self._wrapper = list
        return value[0] if count(tell) == 1 else value

    def get(self):
        '''
        Return outgoing things wrapped with :meth:`wrap`.

        .. note::

          With only one outgoing thing, only that one outgoing thing is
          returned. With multiple outgoing things, they are returned wrapped
          with the wrapper assigned with :meth:`wrap` (default wrapper is
          :func:`list`).
        '''
        tell, self._out, out = tee(self._out, 3)
        wrap = self._wrapper
        value = list(wrap(i) for i in out) if self._each else wrap(out)
        # reset each flag
        self._each = False
        # reset wrapper
        self._wrapper = list
        return value[0] if count(tell) == 1 else value


class lazyknife(
    _LazyMixin, KnifeMixin, FilterMixin, MapMixin, ReduceMixin, OrderMixin,
    RepeatMixin, MathMixin, SliceMixin, CmpMixin,
):

    '''
    Lazier evaluated combo knife. Features every :mod:`knife` method.

    .. note::

      Also aliased as :class:`~knife.__` when imported from :mod:`knife`.

    >>> from knife import __
    '''

    __slots__ = SLOTS


class cmpknife(_LazyMixin, KnifeMixin, CmpMixin):

    '''
    Lazier evaluated comparing knife. Provides comparison operations for
    incoming things.

    >>> from knife.lazy import cmpknife
    '''

    __slots__ = SLOTS


class filterknife(_LazyMixin, KnifeMixin, FilterMixin):

    '''
    Lazier evaluated filtering knife. Provides filtering operations for
    incoming things.

    >>> from knife.lazy import filterknife
    '''

    __slots__ = SLOTS


class mapknife(_LazyMixin, KnifeMixin, MapMixin):

    '''
    Lazier evaluated mapping knife. Provides `mapping <http://docs.python.org
    /library/functions.html#map>`_ operations for incoming things.

    >>> from knife.lazy import mapknife
    '''

    __slots__ = SLOTS


class mathknife(_LazyMixin, KnifeMixin, MathMixin):

    '''
    Lazier evaluated mathing knife. Provides numeric and statistical
    operations for incoming things.

    >>> from knife.lazy import mathknife
    '''

    __slots__ = SLOTS


class orderknife(_LazyMixin, KnifeMixin, OrderMixin):

    '''
    Lazier evaluated ordering knife. Provides sorting and grouping operations
    for incoming things.

    >>> from knife.lazy import orderknife
    '''

    __slots__ = SLOTS


class reduceknife(_LazyMixin, KnifeMixin, ReduceMixin):

    '''
    Lazier evaluated reducing knife. Provides `reducing <http://docs.python.
    org/library/functions.html#map>`_ operations for incoming things.

    >>> from knife.lazy import reduceknife
    '''

    __slots__ = SLOTS


class repeatknife(_LazyMixin, KnifeMixin, RepeatMixin):

    '''
    Lazier evaluated repeating knife. Provides repetition operations for
    incoming things.

    >>> from knife.lazy import repeatknife
    '''

    __slots__ = SLOTS


class sliceknife(_LazyMixin, KnifeMixin, SliceMixin):

    '''
    Lazier evaluated slicing knife. Provides `slicing <http://docs.python.
    org/library/functions.html#slice>`_ operations for incoming things.

    >>> from knife.lazy import sliceknife
    '''

    __slots__ = SLOTS
