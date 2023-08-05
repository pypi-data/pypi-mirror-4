#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='engineer_number',
    packages=['engineer_number'],
    version='1.0.0',
    description='Engineer Number calculate',
    author='梅どぶろく(umedoblock)',
    author_email='umedoblock@gmail.com',
    url='http://pypi.python.org/pypi/engineer_number/',
    download_url='',
    keywords=['engineer', 'SI'],
    license='BSD License',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    # see
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    options = {
        'sdist': {                                                                          'formats': ['gztar','zip'],
            'force_manifest': True,                                                     },
    },

    long_description = '''\
| Engineer Number calculate
| -------------------------
| 
| This module can easily calculate Engineer Number.
| 
| This version requires Python 3 or later.
| Python 2 version  may be available but no support Python 2 version.
| 
| for example.
| 
| 0.
| >>> from engineer_number import EngineerNumber
| 
| 1.
| >>> nano470 = EngineerNumber('470n')
| >>> nano470
| 470.000n
| >>> nano470['u']
| '0.470u'
| 
| 2.
| >>> c104 = EngineerNumber('10p') * 10 ** 4
| >>> c104['u']
| '0.100u'
| >>> c104['n']
| '100.000n'
| 
| 3.
| >>> G1 = EngineerNumber('1G')
| >>> M103 = EngineerNumber('103M')
| >>> G1 / M103
| 9.709
| 
| 4.
| >>> Vcc = 5
| >>> k47 = EngineerNumber('47k')
| >>> Ibeo = Vcc / k47
| >>> Ibeo
| 106.383u
| >>> Ibeo['m']
| '0.106m'
| >>> Iceo = Ibeo * 140
| >>> Iceo['m']
| '14.894m'
| >>> Io = Ibeo + Iceo
| >>> Io
| 15.000m
| >>> Io['']
| '0.015'
''',
     )
