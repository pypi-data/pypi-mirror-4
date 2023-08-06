import os
from setuptools import setup, find_packages

__version__ = '1.0'

setup(
    name='z3c.recipe.compattest',
    version=__version__,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description='Buildout recipe to create testrunners for testing '
                'compatibility with other packages',
    url='http://pypi.python.org/pypi/z3c.recipe.compattest',
    long_description=(
        '.. contents::'
        + '\n\n'
        + open('CHANGES.rst').read()
        + '\n\n'
        '======================\n'
        'Detailed Documentation\n'
        '======================'
        + '\n\n' +
        open(os.path.join(
            'src', 'z3c', 'recipe', 'compattest', 'README.txt')).read()),
    keywords="zope setuptools egg kgs",
    classifiers=[
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c', 'z3c.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout >= 2.0.0',
        'zc.recipe.testrunner >= 2.0.0',
    ],
    # zope.dottedname is just used as a dummy package to demonstrate things
    # with, it's not actually imported
    extras_require=dict(test=[
        'zope.dottedname',
        'zope.testing',
        'manuel',
        'six',
    ]),
    entry_points={
        'zc.buildout': ['default = z3c.recipe.compattest.recipe:Recipe'],
    },
    include_package_data=True,
    zip_safe=False,
)
