"""
ncutils
----------

ncutils is a python module for niconico douga. You can install via pip/easy_install. Have fun!

Documents and other resources are available at `github <https://github.com/sakamotomsh/ncutils>`_ . 

Releases
~~~~~~~~~~
- 0.3.0 (2012-10-08)
    - Added ncsh, interactive shell for niconico douga
    - Improved tests
- 0.2.1 (2012-09-10)
    -  Use setuptools to distribute scripts
- 0.2.0 (2012-09-09)
    - Support for Windows
    - Added some scripts
- 0.1.0 (2012-08-25)
    - Initial Release
"""

#for tests
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["tests"]
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

from setuptools import setup
setup(
    name='ncutils',
    version='0.3.0',
    url='https://github.com/sakamotomsh/ncutils',
    license='BSD',
    author='sakamotomsh',
    author_email='sakamotomsh@lolloo.net',
    description='niconico douga module',
    long_description=__doc__,
    packages=['ncutils', ],

    entry_points={
        "console_scripts": [
            "ncsh               = ncutils.ncsh:main",
            "nc_download        = ncutils.recipes:download_video",
            "nc_download_mylist = ncutils.recipes:download_video_in_mylist",
            "nc_queue_consume   = ncutils.recipes:download_video_and_remove_entry_from_mylist",
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Utilities'
    ],

    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)
