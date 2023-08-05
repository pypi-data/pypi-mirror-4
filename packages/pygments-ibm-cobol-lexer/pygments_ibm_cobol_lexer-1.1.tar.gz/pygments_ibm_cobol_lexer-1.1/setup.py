from setuptools import setup, find_packages

setup(name="pygments_ibm_cobol_lexer",
      version="1.1",
      author='Denis Wallerich',
      author_email='denis.wallerich@datim.fr/pygments_ibm_cobol_lexer',
      url = "http://www.datim.fr",
      packages=find_packages(),
      include_package_data=True,
      license='BSD',
      description = 'Cobol IBM Mainframe syntax lexer for Pygments',
      long_description=open('README.rst').read(),
      install_requires=['pygments'],
      entry_points = {
        'pygments.lexers': ['ibmcobol = pygments_ibm_cobol_lexer:IBMCOBOLLexer'],
        'pygments.styles': ['ibmcobol = pygments_ibm_cobol_lexer:IBMCOBOLStyle'],
       },
      )

