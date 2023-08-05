from setuptools import setup, find_packages

DESCRIPTION = 'Python-based SASS Compiler'

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

setup(name='rapydcss',
      packages=['rapydcss_scripts'],
      package_data={'rapydcss_scripts': ['*.sass']},
      author='Alexander Tsepkov',
      author_email='atsepkov@pyjeon.com',
      url='http://www.pyjeon.com/',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      license='GNU GPL3',
      install_requires=['pyScss>=1.1.4'],
      scripts=['rapydcss'],
)
