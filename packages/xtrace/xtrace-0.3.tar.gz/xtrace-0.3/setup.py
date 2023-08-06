from distutils.core import setup

from xtrace import __version__

setup(
    name='xtrace',
    version=__version__,
    author='anatoly techtonik <techtonik@gmail.com>',
    url='http://bitbucket.org/techtonik/xtrace/',

    description="Produce function trace for Python code in Xdebug format",
    license="Public Domain",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Utilities',
    ],

    py_modules=['xtrace'],

    long_description=open('README').read()
)
