# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

try:
    from setuptools import setup
except:
    from distutils.core import setup


VERSION = '0.1'

README = open('README.rst').read()

setup(
    name='mach',
    description='Generic command line command dispatching framework.',
    long_description=README,
    license='MPL 2.0',
    author='Gregory Szorc',
    author_email='gregory.szorc@gmail.com',
    url='https://github.com/indygreg/mach',
    packages=['mach'],
    version=VERSION,
    classifiers=[
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
    ],
    install_requires=['mozprocess', 'blessings'],
)

