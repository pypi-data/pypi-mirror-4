"""
eukalypse_brew is a toolbox for quick n dirty website testing

if lxml fails to install, take a look at http://stackoverflow.com/questions/5178416/pip-install-lxml-error

"""

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys
from setuptools import find_packages


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

install_requires = [
    'requests',
    'lxml',
    'furl',
    'beautifulsoup4',
]


setup(
    name="eukalypse_brew",
    author="Dennis Schwertel",
    author_email="s@digitalkultur.net",
    version='0.1',
    url='https://github.com/kinkerl/eukalypse_brew',
    #license='MIT',
    zip_safe=False,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='quick and dirty website testing toolbox',
    long_description=__doc__,
    install_requires=install_requires,
    tests_require=['tox'],
    cmdclass={'test': Tox},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ]
)
