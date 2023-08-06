from setuptools import find_packages, setup
from setuptools.extension import Extension
import fnmatch
import os.path
import sys


def read_project_version(package):
    py = os.path.join(package, '__init__.py')
    __version__ = None
    for line in open(py).read().splitlines():
        if '__version__' in line:
            exec(line)
            break
    return __version__

NAME = 'pysimavr'
URL = 'https://github.com/ponty/pysimavr'
DESCRIPTION = 'python wrapper for simavr which is AVR and arduino simulator.'
VERSION = read_project_version(NAME)

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

classifiers = [
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
]

install_requires = open("requirements.txt").read().split('\n')


def listdir(directory, pattern):
    names = os.listdir(directory)
    names = fnmatch.filter(names, pattern)
    return [os.path.join(directory, child) for child in names]


def files(directory, pattern):
    return [p for p in listdir(directory, pattern) if os.path.isfile(p)]


def part(name):
    return Extension(name='pysimavr.swig._' + name,
                     sources=[
                     'pysimavr/swig/parts/' + name + '.c',
                     'pysimavr/swig/' + name + '.i',
#                     'pysimavr/swig/sim/sim_cycle_timers.c',
#                     'pysimavr/swig/sim/sim_irq.c',
#                     'pysimavr/swig/sim/sim_io.c',
                     ],
                     libraries=['elf'],
                     include_dirs=[
                     'pysimavr/swig/sim',
                     'pysimavr/swig/include',
                     'pysimavr/swig/parts',
                     ],
                     swig_opts=[
                     #                       '-modern',
                     '-Ipysimavr/swig/parts',
                     '-Ipysimavr/swig/sim',
                     ],
                     extra_compile_args=[
                     '--std=gnu99',
                     ],
                     )

ext_modules = [
    Extension(name='pysimavr.swig._simavr',
              sources=[
              'pysimavr/swig/simavr.i',
              'pysimavr/swig/simavr_logger.cpp',
              ]
              + files('pysimavr/swig/sim', '*.c')
              + files('pysimavr/swig/cores', 'sim_*.c'),
              libraries=['elf'],
              include_dirs=[
              'pysimavr/swig/sim',
              'pysimavr/swig/include',
              ],
              swig_opts=[
              #                       '-modern',
              '-Ipysimavr/swig/sim',
              ],
              extra_compile_args=[
              '--std=gnu99',
              '-DNO_COLOR',
              ],
              ),
    part('sgm7'),
    part('ledrow'),
    part('inverter'),
    part('hd44780'),
    part('ac_input'),
    part('button'),
    part('uart_udp'),
    part('spk'),
    part('uart_buff'),
    
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst', 'r').read(),
    classifiers=classifiers,
    keywords='avr simavr',
    author='ponty',
    # author_email='',
    url=URL,
    license='GPL',
    packages=find_packages(exclude=['bootstrap', 'pavement', ]),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    ext_modules=ext_modules,
    **extra
)
