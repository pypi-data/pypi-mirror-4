# -*- coding: utf-8 -*-
'''Base knife mixins.'''

from operator import truth
from threading import local
from functools import partial
from collections import deque

from stuf.utils import memoize
from stuf.patterns import searcher
from stuf.six import identity, tounicode, tobytes

SLOTS = (
    '_in _work _hold _out _original _baseline _each _kw _history _worker _args'
    '_wrapper _pipe'
).split()


class KnifeMixin(local):

    '''Base knife mixin.'''

    _REPR = (
        '{0}.{1} ([\nIN: ({2}) =>\nWORK: ({3}) =>\nHOLD: ({4}) =>\nOUT: '
        '({5})\n])'.format
    )

    def __init__(self, ins, outs, **kw):
        super(KnifeMixin, self).__init__()
        # incoming things
        self._in = ins
        # outgoing things
        self._out = outs
        # pipe out default
        self._pipe = None
        # default output default
        self._each = False
        # original and baseline snapshots
        self._original = self._baseline = None
        # maximum number of history snapshots to keep (default: 5)
        self._history = deque(maxlen=kw.pop('snapshots', 5))
        # worker default
        self._worker = None
        # position arguments default
        self._args = ()
        # keyword arguments default
        self._kw = {}
        # default wrapper default
        self._wrapper = list

    @property
    def _identity(self):
        # use  generic identity function for worker if no worker assigned
        return self._worker if self._worker is not None else identity

    @property
    def _test(self, truth_=truth):
        # use truth operator function for worker if no worker assigned
        return self._worker if self._worker is not None else truth_

    @staticmethod
    @memoize
    def _pattern(pat, type, flags, s=searcher):
        # compile glob pattern into regex
        return s((type, pat), flags)

    def apply(self, worker, *args, **kw):
        '''
        Assign :func:`callable` used to work on incoming things plus any
        :term:`positional argument`\s and :term:`keyword argument`\s
        it will use.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever :func:`apply` is
          called.

        :argument worker: a :func:`callable`

        :rtype: :mod:`knife` :term:`object`
        '''
        # assign worker
        self._worker = worker
        # positional params
        self._args = args
        # keyword arguemnts
        self._kw = kw
        return self

    def worker(self, worker):
        '''
        Assign :func:`callable` used to work on incoming things.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever a new `worker` is
          assigned.

        :argument worker: a :func:`callable`

        :rtype: :mod:`knife` :term:`object`
        '''
        # reset stored position params
        self._args = ()
        # reset stored keyword params
        self._kw = {}
        # assign worker
        self._worker = worker
        return self

    def params(self, *args, **kw):
        '''
        Assign :term:`positional argument`\s and :term:`keyword argument`\s
        to be used globally.

        :rtype: :mod:`knife` :term:`object`
        '''
        # positional params
        self._args = args
        # keyword arguemnts
        self._kw = kw
        return self

    def partial(self, worker, *args, **kw):
        self._worker = partial(worker, *args, **kw)
        return self

    def pattern(self, pattern, type='parse', flags=0):
        '''
        Compile search `pattern` for use as :meth:`worker`.

        .. note::

          Global :term:`positional argument`\s and :term:`keyword argument`\s
          assigned with :meth:`params` are reset whenever a new `pattern` is
          compiled.

        :argument str pattern: search pattern

        :keyword str type: engine to compile `pattern` with. Valid options
          are `'parse' <http://pypi.python.org/pypi/parse/>`_, `'re'
          <http://docs.python.org/library/re.html>`_, or `'glob' <http://docs.
          python.org/library/fnmatch.html>`_
        :keyword int flags: regular expression `flags <http://docs.python.org/
          library/re.html#re.DEBUG>`_

        :rtype: :mod:`knife` :term:`object`

        >>> # using parse expression
        >>> test = __('first test', 'second test', 'third test')
        >>> test.pattern('first {}').filter().get()
        'first test'
        >>> # using glob pattern
        >>> test.original().pattern('second*', type='glob').filter().get()
        'second test'
        >>> # using regular expression
        >>> test.original().pattern('third .', type='regex').filter().get()
        'third test'
        '''
        # reset stored position params
        self._args = ()
        # reset stored keyword params
        self._kw = {}
        self._worker = self._pattern(pattern, type, flags)
        return self

    def wrap(self, wrapper):
        '''
        Assign :term:`object`, :term:`type`, or :keyword:`class` used to wrap
        outgoing things.

        .. note::

          A :mod:`knife` :term:`object` resets back to its default wrapper
          (:func:`list`) after :meth:`get` or :meth:`peek` is called.

        :argument wrapper: an :term:`object`, :func:`type`, or :keyword:`class`

        :rtype: :mod:`knife` :term:`object`

        >>> __(1, 2, 3, 4, 5, 6).wrap(tuple).peek()
        (1, 2, 3, 4, 5, 6)
        '''
        self._wrapper = wrapper
        return self

    def oneach(self):
        '''
        Toggle whether each outgoing thing should be individually wrapped with
        the wrapper assigned with :meth:`wrap` (default wrapper is :func:`list`
        ) or whether all outgoing things should be wrapped all at once.

        .. note::

          :mod:`knife` :term:`object` default behavior is to wrap all outgoing
          things all at once. :mod:`knife` :term:`object`\s reset back to this
          behavior **after** :meth:`get` or :meth:`peek` is called.

        :rtype: :mod:`knife` :term:`object`
        '''
        self._each = not self._each
        return self

    def ascii(self, errors='strict'):
        '''
        :meth:`~str.encode` outgoing things as `bytes <http://docs.python
        .org/py3k/library/functions.html#bytes>`_ with the ``'latin-1'`` codec.

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for encoding

        :rtype: :mod:`knife` :term:`object`

        >>> from stuf.six import u, b
        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.ascii().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''
        self._wrapper = lambda x: tobytes(x, 'latin_1', errors)
        return self

    def bytes(self, encoding='utf_8', errors='strict'):
        '''
        :meth:`~str.encode` outgoing things as `bytes <http://docs.python
        .org/py3k/library/functions.html#bytes>`_.

        :keyword str encoding: character `encoding <http://docs.python.org/
          library/codecs.html#standard-encodings>`_

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for encoding

        :rtype: :mod:`knife` :term:`object`

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.bytes().oneach().peek()
        ['[1]', 'True', 't', 'i', 'g', 'None', '(1,)']
        '''
        self._wrapper = lambda x: tobytes(x, encoding, errors)
        return self

    def unicode(self, encoding='utf_8', errors='strict'):
        '''
        :func:`unicode` (:func:`str` under Python 3) :meth:`~str.decode`
        outgoing things.

        :keyword str encoding: Unicode `encoding <http://docs.python.org/
          library/codecs.html#standard-encodings>`_

        :keyword str errors: `error handling <http://docs.python.org/library/
          codecs.html#codec-base-classes>`_ for decoding

        :rtype: :mod:`knife` :term:`object`

        >>> test = __([1], True, r't', b('i'), u('g'), None, (1,))
        >>> test.unicode().oneach().peek()
        [u'[1]', u'True', u't', u'i', u'g', u'None', u'(1,)']
        '''
        self._wrapper = lambda x: tounicode(x, encoding, errors)
        return self
