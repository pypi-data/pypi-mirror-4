`knife` is a powerful `Python <http://docs.python.org/>`_ multitool
loosely inspired by `Underscore.js <http://documentcloud.github.com/underscore/>`_
but remixed for maximum `pythonicity <http://docs.python.org/glossary.html#term-pythonic>`_. 

`knife` concentrates power that is normally dispersed across the entire
Python universe in one convenient shrink-wrapped package.

Vitals
======

`knife` works with CPython 2.6, 2.7, 3.1. and 3.2 and PyPy 1.8.

`knife` documentation is at http://readthedocs.org/docs/knife/en/latest/ or
http://packages.python.org/knife/

Installation
============

Install `knife` with `pip <http://www.pip-installer.org/en/latest/index.html>`_...::

  $ pip install knife
  [... possibly exciting stuff happening ...]
  Successfully installed knife
  
...or `easy_install <http://packages.python.org/distribute/>`_...::

  $ easy_install knife
  [... possibly exciting stuff happening ...]
  Finished processing dependencies for knife
  
...or old school by downloading `knife` from http://pypi.python.org/pypi/knife/::

  $ python setup.py install
  [... possibly exciting stuff happening ...]
  Finished processing dependencies for knife

Development
===========

 * Public repository: https://bitbucket.org/lcrees/knife.
 * Mirror: https://github.com/kwarterthieves/knife/
 * Issue tracker: https://bitbucket.org/lcrees/knife/issues
 * License: `BSD <http://www.opensource.org/licenses/bsd-license.php>`_

3 second *knife*
================

Things go in:

  >>> from knife import __
  >>> gauntlet = __(5, 4, 3, 2, 1)
  
Things get knifed:

  >>> gauntlet.initial().rest().slice(1, 2).last()
  knife.lazy.lazyknife ([IN: ([3]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])

Things come out:

  >>> gauntlet.get()
  3

Slightly more *knife*
=====================

`knife` has 40 plus methods that can be `chained <https://en.wikipedia.org/
wiki/Fluent_interface>`_ into pipelines...

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> __(5, 4, 3, 2, 1).initial().rest().slice(1, 2).last().get()
  3

...or used object-oriented style.

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> from knife import knife
  >>> oo = knife(5, 4, 3, 2, 1)
  >>> oo.initial()
  knife.active.activeknife ([IN: ([5, 4, 3, 2, 1]) => WORK: ([]) => HOLD: ([]) => OUT: ([5, 4, 3, 2])])
  >>> oo.rest()
  knife.active.activeknife ([IN: ([5, 4, 3, 2]) => WORK: ([]) => HOLD: ([]) => OUT: ([4, 3, 2])])
  >>> oo.slice(1, 2)
  knife.active.activeknife ([IN: ([4, 3, 2]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])
  >>> oo.last()
  knife.active.activeknife ([IN: ([3]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])
  >>> oo.get()
  3
  
A `knife` object can roll its current state back to previous states
like snapshots of immediately preceding operations, a baseline snapshot, or even 
a snapshot of the original arguments.

contrived example:
^^^^^^^^^^^^^^^^^^
  
  >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
  >>> undone.peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.append(1).undo().peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.append(1).append(2).undo(2).peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.snapshot().append(1).append(2).baseline().peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.original().peek()
  [1, 2, 3]

`knife` objects come in two flavors: `active` and `lazy`.
`active.knife` objects evaluate the result of calling a
method immediately after the call. Calling the same method with
a `lazy.knife` object only yields results when it is iterated over
or `knife.lazy.lazyknife.get` is called to get results.
  
`knife.lazy.lazyknife` combines all `knife` methods in one class:

  >>> from knife import lazyknife

It can be imported under its *dunderscore* (`knife.__`) alias.

  >>> from knife import __  
  
`knife.active.activeknife` also combines every `knife` method in one
combo `knife` class:

  >>> from knife import activeknife

It can be imported under its `knife.knife` alias:
 
  >>> from knife import knife

`knife` methods are available in more focused classes that group related 
methods together. These classes can also be chained into pipelines.

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> from knife.active import mathknife, reduceknife
  >>> one = mathknife(10, 5, 100, 2, 1000)
  >>> two = reduceknife()
  >>> one.minmax().pipe(two).merge().back().min().get()
  2
  >>> one.original().minmax().pipe(two).merge().back().max().get()
  1000
  >>> one.original().minmax().pipe(two).merge().back().sum().get()
  1002