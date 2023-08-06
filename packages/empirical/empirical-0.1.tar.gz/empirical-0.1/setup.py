import os

from setuptools import setup, find_packages

README = open('README.txt').read()
THANKS = open('THANKS.txt').read()
CHANGES = open('CHANGES.txt').read()
full_description = README + '\n\n' + THANKS + '\n\n' + CHANGES

requires = [
    'numpy >= 1.7',
    'scipy >= 0.11',
    'matplotlib >= 1.2.1',
    ]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development",
    ]


setup(name='empirical',
      version='0.1',
      description='Emperical Method of Fundamental Solutions solver for Python.',
      long_description=full_description,
      classifiers=classifiers,
      author='D. Ryan Hild',
      author_email='d.ryan.hild@gmail.com',
      url='http://pypi.python.org/pypi/empirical/',
      packages=find_packages(),
      license='GPLv3',
      include_package_data=True,
      install_requires=requires,
      )
