from setuptools import setup, find_packages

DESCRIPTION = 'Python-based SASS Compiler'

LONG_DESCRIPTION = """
RapydCSS
===========

RapydCSS is a wrapper around PyScss, which is a Python
implementation of SASS. RapydCSS adds support for indented
syntax to PyScss, which SASS already has.


Installation
------------
To install RapydCSS simply use easy_install or pip:

    pip install rapydcss

or

    easy_install rapydcss


License
-------
The project is GPLv3, but the output is license free. 
See http://www.gnu.org/licenses/gpl-faq.html#WhatCaseIsOutputGPL.

"""

setup(name='rapydcss',
      version='0.0.1',
      packages=['rapydcss'],
      package_data={'rapydcss': ['*.sass']},
      author='Alexander Tsepkov',
      url='http://www.pyjeon.com/rapydcss',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      license='GNU GPL3',
      install_requires=['pyScss>=1.1.4'],
      scripts=['bin/rapydcss']
)

