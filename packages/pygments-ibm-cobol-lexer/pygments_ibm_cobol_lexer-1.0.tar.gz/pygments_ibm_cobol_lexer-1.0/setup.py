
"""Description:  Cobol IBM Mainframe syntax lexer for Pygments
        
        This package contains a Pygments Lexer for cobol  (db2, cics and dli embedded) 
        
        Many early programming languages, including Fortran, Cobol and the various IBM assembler languages,
        used only the first 7-72 columns of a 80-column card

       ### MAINFRAME COBOL CODING FORM:
           ---------------------------
           Columns
           1- 6       Tags, Remarks or Sequence numbers identifying pages or lines of a program
           7          Continuation, comment or starting of a new page
           8 - 72     COBOL program statements
           73- 80     Tags, Remarks or Sequence numbers (often garbage...)
  
           =>    Column 7  * (asterisk) designates entire line as comment
                    / (slash) forces page break when printing source listing
                    - (dash) to indicate continuation of nonnumeric literal
           =>    Columns 8-72 divided into two areas
                 - Area A - columns 8 to 11
                 - Area B - columns 12 to 72
           
           Division, section and paragraph-names must all begin in Area A and end with a period.
           CBL/PROCESS statement can start in columns 1 through 70
       
       ### Installation
        
           The lexer is available as a Pip package:
        
           pip install pygments_ibm_cobol_lexer
        
       ### Usage
        
           After installation the ibmcobol Lexer and ibmcobol Style automatically registers itself for files with the ".cbl"
           extensions. Therefore, usage is easy:
        
           - pygmentize -O full,linenos=tab,style=ibmcobol -o test.html HORREUR.cbl
           - pygmentize -O full,encoding=iso8859-1,outencoding=latin1,linenos=tab,style=ibmcobol -o HORREUR.html HORREUR.cbl
"""


from setuptools import setup, find_packages


doclines = __doc__.split("\n")


setup(name="pygments_ibm_cobol_lexer",
      version="1.0",
      author='Denis Wallerich',
      author_email='denis.wallerich@datim.fr',
      url = "http://www.datim.fr",
      packages=["pygments_ibm_cobol_lexer"],
      license='BSD',
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      install_requires=['pygments'],
      entry_points = {
        'pygments.lexers': ['ibmcobol = pygments_ibm_cobol_lexer:IBMCOBOLLexer'],
        'pygments.styles': ['ibmcobol = pygments_ibm_cobol_lexer:IBMCOBOLStyle'],
       },
      package_data={'pygments_ibm_cobol_lexer': ['test/*.cbl','test/*.html','test/*.css']},
      )

