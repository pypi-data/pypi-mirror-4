import doctest
import re
import zc.buildout.testing
from zope.testing import renormalizing


normalize_script = (re.compile('(-  [a-zA-Z0-9_.-]+)-script.py\n'), '\\1\n')
normalize_exe = (re.compile('-  [a-zA-Z0-9_.-]+.exe\n'), '')

# Distribute does not result in a setuptools compattest binary, so filter
# that out.
normalize_setuptools = (
    re.compile('-  compattest-setuptools'),
    '')

# On windows and OS X the name of the python executable starts with a
# capital 'P'. On linux it does not.
python_case_normalizer = (re.compile('[pP]ython'), 'python')


def DocFileSuite(*args, **kw):
    def setUp(test):
        zc.buildout.testing.buildoutSetUp(test)
        zc.buildout.testing.install_develop('z3c.recipe.compattest', test)

        # need to explicitly name our dependencies for the buildout test
        # environment
        zc.buildout.testing.install('zc.recipe.testrunner', test)
        zc.buildout.testing.install('zc.recipe.egg', test)
        zc.buildout.testing.install('zope.testing', test)
        zc.buildout.testing.install('zope.testrunner', test)
        zc.buildout.testing.install('zope.interface', test)
        zc.buildout.testing.install('zope.exceptions', test)
        zc.buildout.testing.install('zope.dottedname', test)
        zc.buildout.testing.install('manuel', test)
        zc.buildout.testing.install('six', test)

    def tearDown(test):
        zc.buildout.testing.buildoutTearDown(test)

    kw['setUp'] = setUp
    kw['tearDown'] = tearDown
    kw['optionflags'] = (doctest.ELLIPSIS
                         | doctest.NORMALIZE_WHITESPACE)
    kw['checker'] = renormalizing.RENormalizing([
        zc.buildout.testing.normalize_path,
        normalize_script,
        normalize_exe,
        normalize_setuptools,
        python_case_normalizer,
    ])

    return doctest.DocFileSuite(*args, **kw)
