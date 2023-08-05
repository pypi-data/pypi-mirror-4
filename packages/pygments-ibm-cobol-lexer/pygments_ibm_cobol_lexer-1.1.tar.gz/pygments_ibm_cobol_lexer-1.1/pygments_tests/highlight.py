#!/usr/bin/python
# coding: utf-8
from os.path import abspath
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments_ibm_cobol_lexer import IBMCOBOLLexer, IBMCOBOLStyle


## cp1147 test:
#from pygments_ibm_cobol_lexer import cp1147
#print "euro sign ?",chr(159).decode('cp1147')
#print ''.join([ chr(i).decode('cp1147') for i in range(0,256)
#          if chr(i).decode('cp1147') != chr(i).decode('cp500')])

my_code = open("COB001.cp1147.cbl",'rb').read()
html='COB001.html'
lexer=IBMCOBOLLexer(encoding='cp1147')
formatter=HtmlFormatter(style=IBMCOBOLStyle
                        ,encoding='latin1'
                        ,full=True
                        #,cssfile='ibmcob.css'
                        ,title='Test pygments IBM Cobol Lexer '
                        ,monofont=True)
highlight(my_code
         ,lexer
         ,formatter
         ,open(test,'wb'))

print "file://"+abspath(html),
    
