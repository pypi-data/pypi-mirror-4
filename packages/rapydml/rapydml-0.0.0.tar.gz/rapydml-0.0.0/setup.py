from setuptools import setup, find_packages

DESCRIPTION = 'Python-based XML/HTML Compiler'

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.text').read()
except:
    pass

setup(name='rapydml',
      packages=['rapydml_scripts'],
      package_data={'rapydml_scripts': ['*.txt', 'lib/*', 'markup/*']},
      author='Alexander Tsepkov',
      author_email='atsepkov@pyjeon.com',
      url='http://www.pyjeon.com/',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      platforms=['any'],
      license='GNU GPL3',
      install_requires=[],
      scripts=['rapydml'],
)
