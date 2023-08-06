=======
CHANGES
=======

1.0 (2013-03-02)
================

- Depend on buildout 2 and zc.recipe.testrunner 2.


0.13.1 (2010-12-17)
===================

- Fix tests on windows.

- Fix for use with a python executable from inside a virtualenv.


0.13 (2010-10-07)
=================

- Depend on and use the new features of the zc.buildout 1.5 line. At the same
  time support for zc.buildout <= 1.5.1 has been dropped.

- Updated test set up, to run with newer ``zope.testing`` version which no
  longer includes testrunner.

- The z3c.recipe.scripts.scripts recipe behind zc.recipe.testrunner.TestRunner
  does not accept plain dicts anymore, so we wrap the options in a
  _BackwardsSupportOptions object. Ideally this should've use an official
  API though.

0.12.2 (2010-02-24)
===================

- Moved the gathering of include-dependencies from the __init__ to the update
  method to prevent installing dependencies before other buildout parts could
  do their job.

0.12.1 (2009-12-15)
===================

- Fixed bug in using exclude introduced in 0.12 (including test to make sure
  it doesn't happen again).


0.12 (2009-12-14)
=================

- Added ``include-dependencies`` option that automatically includes the
  dependencies of the specified packages.  Very handy to get an automatically
  updated list of those packages that are most useful to test: all our
  dependencies.


0.11 (2009-09-30)
=================

- Removed the "check out packages from subversion" feature.
  If you require such functionality, mr.developer
  <http://pypi.python.org/pypi/mr.developer> provides this much more
  comprehensively (and for multiple version control systems, too) .

0.10 (2009-09-28)
=================

- Options prefixed by ``runner-`` are automatically passed to generated test
  runners.

0.9 (2009-09-14)
================

- Test runner: return the exit code 1 in case of test failures; this simplifies
  buildbot configurations.

0.8 (2009-08-17)
================

- Windoes is now supported.

- Changed the default master script name to the part name. (Don't add
  a "test-" prefix any more.)

0.7 (2009-08-13)
================

- Simplified building the list of packages even more: we now just take a list of
  packages, period.

0.6 (2009-08-07)
================

- Restructured the way we construct our list of packages to test:
  We no longer filter a list we retrieved from SVN with includes/excludes,
  but use an explicit list that can be populated from a buildout section,
  e. g. [versions]. Thus, we can now easily test against a KGS.
- Always enable all extras of packages under test.

0.5 (2009-01-29)
================

- Fix duplicate `url` parameter in setup.py that confused Python 2.4 but
  got accepted by Python 2.5.

0.4 (2009-01-29)
================

- Ignore missing package releases for packages listed in Subversion (as
  long as we don't try to run from Subversion).

- Allow parallel execution of the individual test runners by stating
  'max_jobs=X' in the recipe's options.

0.3 (2009-01-28)
================

- Adding the exclude parameter in buildout causes the default exclude
  list to be merged with the option in buildout.cfg.

0.2 (2009-01-28)
================

- Implemented use_svn option to use SVN trunk checkouts instead of released
  versions.

0.1 (2009-01-28)
================

- first released version
