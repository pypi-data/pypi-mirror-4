=====================
z3c.recipe.compattest
=====================

This buildout recipe generates a list of packages to test and a test runner
that runs each package's tests (isolated from any other tests).
This is useful to check that the changes made while developing a package
do not break any packages that are using this package.

Usage
=====

Add a part to your buildout.cfg that uses this recipe.
No further configuration is required, but you can set the following options:

- ``include``: list of packages to include (whitespace-separated)
  (default: empty)
- ``include-dependencies``: list of packages to include *including* their
  direct dependencies.  (default: empty)
- ``exclude``: packages matching any regex in this list will be excluded
  (default: empty)
- ``script``: the name of the runner script (defaults to the part name)

>>> cd(sample_buildout)
>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... """)

>>> 'Installing compattest' in system(buildout)
True

Details
=======

The recipe generates a test runner for each package, as well as a global runner
script (called `test-compat` by default) that will run all of them:

>>> ls('bin')
- buildout
- compattest
- compattest-z3c.recipe.compattest

>>> cat('bin', 'compattest')
#!...python...
...main(...compattest-z3c.recipe.compattest...

We take care about installing the test dependencies for the packages
(from their ``extras_require['test']``). Do demonstrate this, we
declared a (superfluous) test dependency on ``zope.dottedname``, which is
picked up:

>>> try:
...     print('start')
...     cat('parts', 'compattest-z3c.recipe.compattest', 'site-packages', 'site.py')
... except IOError:
...     print('start')
...     # When the tests are run from a virtualenv, the bin scripts are created
...     # in a different location.
...     cat('bin', 'compattest-z3c.recipe.compattest')
start
...zope.dottedname...

If we use ``include-dependencies`` instead of just ``include``, our direct
dependencies are also picked up, for instance zc.buildout:

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include-dependencies = z3c.recipe.compattest
... """)
>>> print('start', system(buildout))
start...
Generated script '/sample-buildout/bin/compattest-zc.buildout'.
...
Generated script '/sample-buildout/bin/compattest'...

All our direct dependencies have a test script now:

>>> ls('bin')
- buildout
- compattest
- compattest-z3c.recipe.compattest
- compattest-zc.buildout
- compattest-zc.recipe.testrunner

And if you want to exclude one of the automatically included dependencies, use
the ``exclude`` option:

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include-dependencies = z3c.recipe.compattest
... exclude = zc.buildout
... """)
>>> print('start', system(buildout))
start...
Generated script '/sample-buildout/bin/compattest'...

``bin/compattest-zc.buildout`` is now missing:

>>> ls('bin')
- buildout
- compattest
- compattest-z3c.recipe.compattest
- compattest-zc.recipe.testrunner



Passing options to the test runners
===================================

If you want to use custom options in the generated test runners, you can specify
them in the part options, prefixed by ``runner-``. That is, if you want to pass
the ``--foo`` option by default to all generated test runners, you can set
``runner-defaults = ['--foo']`` in your part:

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... runner-defaults = ['-c', '-v', '-v']
... """)
>>> ignore = system(buildout)
>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!...python...
...run(...['-c', '-v', '-v']...

Every options prefixed by ``runner-`` will be automatically passed to the
generated test runners.


Passing Extra paths to the test runners
=======================================

If you want to add some paths to the generated test runners, you can do it with
the extra-paths option in the part. This might be interesting if you want to test packages
that depends on zope2 < 2.12:

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... extra-paths = zope2location/lib/python
... """)
>>> ignore = system(buildout)
>>> try:
...     print('start')
...     cat('parts', 'compattest-z3c.recipe.compattest', 'site-packages', 'site.py')
... except IOError:
...     print('start')
...     # When the tests are run from a virtualenv, the bin scripts are created
...     # in a different location.
...     cat('bin', 'compattest-z3c.recipe.compattest')
start
...zope2location/lib/python...
