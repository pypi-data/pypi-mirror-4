# -*- coding: utf-8 -*-
import re
from pygments.lexer import RegexLexer, include, bygroups, using, this
from pygments.token import Text, Other, Whitespace, Keyword, Name, Comment, String, \
                           Error, Number, Operator, Generic, Punctuation
from pygments.style import Style

class IBMCOBOLStyle(Style):
    default_style = ""
    background_color = "#111111"
    styles = {
        
        Error:                  'bg:#ff0000 #ffffff',
        Text.Tag:               'bg:#9609e9 border:#777777 #ffffff ',

        # custom tags:
        Text.Scrubol:           'italic #555555',
        Text.ScrubolTag:        'bg:#444444 border:#777777 #ffffff ',
        Text.ScrubolDoc:        '#dcdcdc',
        Text.ScrubolTagDoc:     'bg:#444444 border:#777777 #ffffff ',
        Text.ScrubolWarn:       'italic #555555',
        Text.ScrubolTagWarn:    'bg:#ff0000 border:#ff0000 #ffffff ',

        Comment.MargeLeft:      '#fcff70', 
        Comment.MargeRight:     '#fcff70', 
        Comment:                '#00c8ff',
        Comment.Debug:          '#0000c9',
        Comment.Continuation:   '#9609e9',

        Comment.CicsExec:       '#9609e9',
        Name.Cics:              '#fc9b00',
        Keyword.Cics:           '#fc6b00',
        Punctuation.Cics:       '#b1f603',
        Comment.AllCics:        '#901060',
        Operator.Cics:          '#00d300',

        Comment.DliExec:        '#9609e9',
        Name.Dli:               '#fc9b00',
        Keyword.Dli:            '#fc6b00',
        Punctuation.Dli:        '#b1f603',
        Comment.AllDli:         '#901060',
        Operator.Dli:           '#00d300',
            
        Comment.SqlExec:        '#9609e9',
        Comment.AllSql:         '#900060',
        Keyword.Sql:            '#933493',
        Name.Sql:               '#d898f4',
        Punctuation.Sql:        '#b1f603',
        Operator.Sql:           '#933493',

        Keyword:                '#ff0000',
        Name.Division:          'underline bold #ff0000',
        Name.CompileOpts:       'bold #ff0000',
        Name.Section:           'underline #ff0000',
        Name.Paragraphe:        'underline #00d300',

        Name:                   '#00d300',
        Name.Function:          '#900090',
        Punctuation:            '#b1f603',
        Number:                 '#f9f821',
        Operator:               '#007300',
        String:                 '#ffffff',
    }

DB2_KEYWORDS=[
    "ABSOLUTE","ACCESS","ACTION","ACTIVATE","ADA","ADD","AFTER","ALIAS","ALL","ALLOCATE",
    "ALLOW","ALTER","ALTERIN","ALWAYS","AND","ANY","APPEND","ARE","AS","ASC","ASCII",
    "ASSERTION","ASSOCIATE","ASUTIME","AT","ATOMIC","ATTRIBUTES","AUTHORIZATION",
    "AUTHID","AUTOMATIC","AVG","BEFORE","BEGIN","BETWEEN","BINARY","BIND","BINDADD",
    "BIT","BIT_LENGTH","BLOB","BLOCKED","BOTH","BUFFERPOOL","BUFFERPOOLS","BY",
    "C","CACHE","CALL","CALLED","CALLER","CAPTURE","CARDINALITY","CASCADE","CASCADED",
    "CASE","CAST","CATALOG","CATALOG_NAME","CHANGE","CHANGED","CHANGES","CHAR",
    "CHAR_LENGTH","CHARACTER","CHARACTER_LENGTH","CHECK","CHECKED","CLIENT",
    "CLOB","CLOSE","CLUSTER","COBOL","COLLATE","COLLATION","COLLECT","COLLID","COLUMN",
    "COMMENT","COMMIT","COMMITTED","COMPARISONS","CONCAT","CONDITION","CONDITION_NUMBER",
    "CONNECT","CONNECTION","CONNECTION_NAME","CONSERVATIVE","CONSTRAINT",
    "CONSTRAINTS","CONTAINS","CONTINUE","CONTROL","CONVERT","COPY","CORRELATION",
    "CORR","CORRESPONDING","COUNT","COUNT_BIG","CPU","C\+\+","CREATE","CREATEIN",
    "CREATETAB","CROSS","CUBE","CURRENT","CURRENT_DATE","CURRENT_PATH","CURRENT_SCHEMA",
    "CURRENT_SERVER","CURRENT_SQLID","CURRENT_TIME","CURRENT_TIMESTAMP",
    "CURRENT_TIMEZONE","CURRENT_USER","CURSOR","CURSORS","CURSOR_NAME","CYCLE",
    "DATE","DATA","DATABASE","DATALINK","DAY","DAYS","DB","DBADM","DBCLOB","DBINFO",
    "DB2DARI","DB2GENRL","DB2GENERAL","DB2SQL","DEADLOCKS","DEALLOCATE","DEC",
    "DECIMAL","DECLARE","DEFAULT","DEFAULTS","DEFINE","DEFINITION","DEGREE","DEFER",
    "DEFERRABLE","DEFERRED","DELETE","DESC","DESCRIBE","DESCRIPTOR","DETERMINISTIC",
    "DIAGNOSTICS","DIMENSIONS","DISABLE","DISALLOW","DISCONNECT","DISPATCH",
    "DISTINCT","DOMAIN","DO","DOUBLE","DROP","DROPIN","DYNAMIC","EACH","EBCDIC","ELSE",
    "ELSEIF","EMPTY","ENABLE","END","END-EXEC","ERASE","ESCAPE","EUR","EVENT","EXACT",
    "EXCEPT","EXCEPTION","EXCLUDE","EXCLUDING","EXCLUSIVE","EXEC","EXECUTE","EXISTS",
    "EXIT","EXPLAIN","EXTENDED","EXTENSION","EXTERNAL","EXTRACT","FALSE","FEDERATED",
    "FENCED","FETCH","FILE","FINAL","FIRST","FLOAT","FLUSH","FOLLOWING","FOR","FORCE",
    "FOREIGN","FORTRAN","FOUND","FREEPAGE","FROM","FS","FULL","FUNCTION","G","GBPCACHE",
    "GENERAL","GENERATE","GENERATED","GET","GLOBAL","GO","GOTO","GRANT","GRAPHIC",
    "GROUP","GROUPING","HANDLER","HAVING","HOLD","HOUR","HOURS","IDENTITY","IF","IMMEDIATE",
    "IMPLICIT_SCHEMA","IN","INCLUDE","INCLUDING","INCREMENT","INDEX","INDEXES",
    "INDICATOR","INHERIT","INITIALLY","INITIAL_INSTS","INITIAL_IOS","INNER",
    "INOUT","INPUT","INSENSITIVE","INSERT","INSTEAD","INSTS_PER_ARGBYTE","INSTS_PER_INVOC",
    "INT","INTEGER","INTEGRITY","INTERSECT","INTERVAL","INTO","IOS_PER_ARGBYTE",
    "IOS_PER_INVOC","IS","ISO","ITERATE","ISOLATION","JAVA","JIS","JOIN","K","KEY",
    "KEYS","LANGUAGE","LARGE","LAST","LEADING","LEAVE","LEFT","LENGTH","LEVEL","LIBRARY",
    "LIKE","LIMIT","LINK","LINKTYPE","LOAD","LOCAL","LOCATOR","LOCATORS","LOCK","LOCKS",
    "LOCKSIZE","LOGGED","LONG","LONGVAR","LOOP","LOWER","M","MAINTAINED","MAPPING",
    "MATCH","MAX","MAXVALUE","MESSAGE_TEXT","METHOD","MICROSECOND","MICROSECONDS",
    "MINUTE","MINUTES","MINVALUE","MIXED","MODE","MODIFIES","MODULE","MONITOR",
    "MONTH","MONTHS","MORE","NAMED","NAMES","NATIONAL","NATURAL","NCHAR","NEW","NEW_TABLE",
    "NEXT","NEXTVAL","NICKNAME","NO","NOCACHE","NOCYCLE","NODE","NOMAXVALUE","NOMINVALUE",
    "NONE","NOORDER","NOT","NULL","NULLABLE","NULLS","NUMBER","NUMERIC","OBJECT",
    "OF","OFF","OLD","OLD_TABLE","OLE","OLEDB","ON","ONCE","ONLINE","ONLY","OPEN","OPTIMIZATION",
    "OPTIMIZE","OPTION","OPTIONS","OR","ORDER","OUT","OUTER","OUTPUT","OVER","OVERLAPS",
    "PACKAGE","PAD","PARTIAL","PARALLEL","PARAMETER","PASCAL","PASSTHRU","PASSWORD",
    "PATH","PARTITION","PARTITIONING","PCTFREE","PERCENT_ARGBYTES","PERMISSION",
    "PIECESIZE","PIPE","PLAN","PLI","POSITION","PRECEDING","PRECISION","PREPARE",
    "PRESERVE","PRIMARY","PRIOR","PRIQTY","PRIVILEGES","PROCEDURE","PROGRAM",
    "PROTOCOL","PUBLIC","QUERY","QUERYNO","RANGE","READ","READS","REAL","RECOMMEND",
    "RECOVERY","REF","REFERENCE","REFERENCES","REFERENCING","REFRESH","REGISTERS",
    "RELATIVE","RELEASE","RENAME","REPEATABLE","REPEAT","REPLACE","REPLICATED",
    "RESET","RESIDENT","RESIGNAL","RESOLVE","RESTART","RESTORE","RESTRICT","RESULT",
    "RESULT_SET_LOCATOR","RETURNED_SQLSTATE","RETAIN","RETURN","RETURNS",
    "RETURN_STATUS","REVOKE","RIGHT","ROLLBACK","ROLLUP","ROUTINE","ROW","ROW_COUNT",
    "ROWID","ROWS","RUN","S","SAVEPOINT","SBCS","SCALE","SCHEMA","SCOPE","SCRATCHPAD",
    "SCROLL","SEARCH","SECOND","SECONDS","SECQTY","SECTION","SELECT","SELECTIVITY",
    "SELF","SEQUENCE","SERIALIZABLE","SERVER","SERVER_NAME","SESSION","SESSION_USER",
    "SET","SETS","SHARE","SHRLEVEL","SIGNAL","SIMPLE","SIZE","SMALLINT","SNAPSHOT",
    "SOME","SOURCE","SPACE","SPECIAL","SPECIFIC","SQL","SQLCODE","SQLERROR","SQLEXCEPTION",
    "SQLWARNING","SQLID","SQLSTATE","START","STATE","STATEMENT","STATISTICS",
    "STAY","STOGROUP","STORAGE","STORED","STYLE","SUB","SUBSTRING","SUMMARY","SWITCH",
    "SYNONYM","SYSTEM","SYSTEM_USER","TABLE","TABLES","TABLE_NAME","TABLESPACE",
    "TABLESPACES","TEMPLATE","TEMPORARY","THEN","THREADSAFE","TIME","TIMESTAMP",
    "TIMEZONE","TIMEZONE_HOUR","TIMEZONE_MINUTE","TO","TRAILING","TRANSACTION",
    "TRANSFORM","TRANSLATE","TRANSLATION","TREAT","TRIGGER","TRIM","TRUE","TYPE",
    "UNBOUNDED","UNCOMMITTED","UNDER","UNDO","UNICODE","UNION","UNIQUE","UNKNOWN",
    "UNTIL","UPDATE","UPPER","URL","USA","USE","USAGE","USER","USING","VALUE","VALUES",
    "VARCHAR","VARGRAPHIC","VARIANT","VARYING","VCAT","VERSION","VIEW","VOLATILE",
    "WHEN","WHENEVER","WHERE","WHILE","WITH","WITHOUT","WORK","WRAPPER","WRITE","YEAR",
    "YEARS","YES","ZONE"]

DLI_KEYWORDS=[
    "ACCEPT","DLET","GN","GET","NEXT","GNP","IN","PARENT","GU","UNIQUE","ISRT","INSERT",
    "POS","POSITION","REPL","REPLACE","RETRIEVE","SCHD","SCHEDULE","TERM","TERMINATE",
    "CHKP","CHECKPOINT","DEQ","LOAD","LOG","QUERY","REFRESH","ROLB","ROLL","ROLS","SETS","SETU",
    "STAT","SYMCHKP","XRST"]

CICS_KEYWORDS=[
    "ABCODE","ABEND","ADDRESS","AID","ALARM","ASKTIME","ASSIGN","CANCEL",    
    "COMMAREA","CURSOR","CWA","START","DATA","DATASET","DELETE","DELETEQ","DUMP",    
    "DUMPCODE","DUPKEY","ENDBR","ENDFILE","EQUAL","ERASE","ERROR","FILE",    
    "FLENGTH","FORMATTIME","FREEKB","FREEMAIN","FROM","GENERIC","GETMAIN","GTEQ",    
    "HANDLE","CONDITION","HOLD","IGNORE","INITIMG","INTERVAL","INTO","ISSUE_DISCONNECT",
    "ITEM","ITEMERR","KEYLENGTH","LABEL","LENGERR","LENGTH","OF","LINK","LOAD","MAP",
    "MAPFAIL","MAPSET","NOHANDLE","NOTFND","PROGRAM","QIDERR","QUEUE","RBA","READ",
    "READNEXT","READPREV","READQ_TS","RECEIVE","RETURN","REWRITE","RIDFLD","SEND","TEXT",    
    "SET","SHARED","STARTBR","SYNCPOINT","TERMID","TRANSID","UPDATE","USERID","CONDITION",
    "CURSOR","DISCONNECT","ENDBR","ENDFILE","EQUAL","ERASE","ERROR","FLENGTH","FORMATTIME",
    "FREEKB","FREEMAIN","FROM","GENERIC","GETMAIN","GTEQ","HANDLE","HOLD","IGNORE",    
    "INITIMG","INTERVAL","INTO","ISSUE","ITEM","ITEMERR","KEYLENGTH","LABEL","LENGERR",    
    "LENGTH","LINK","LOAD","MAP","MAPFAIL","MAPSET","NOHANDLE","NOTFND",    
    "OF","PROGRAM","QIDERR","QUEUE","RBA","READ","READNEXT","READPREV","READQ",    
    "RECEIVE","RETURN","REWRITE","REWRITE","RIDFLD","ROLLBACK","SEND","SEND","SET",    
    "SHARED","START","STARTBR","SYNCPOINT","TERMID","TEXT","TRANSID","TS",    
    "UPDATE","USERID","WRITE","WRITEQ","XCTL"]

COBOL_KEYWORDS=[
    "ACCEPT","ACCESS","ADD","ADDRESS","ADVANCING","AFTER","ALL","ALPHABET","ALPHABETIC",
    "ALPHABETIC-LOWER","ALPHABETIC-UPPER","ALPHANUMERIC","ALPHANUMERIC-EDITED",
    "ALSO","ALTER","ALTERNATE","AND","ANY","APPLY","ARE","AREA","AREAS","ASCENDING",
    "ASSIGN","AT","AUTHOR","BACK","BEFORE","BEGINNING","BINARY","BLANK","BLOCK","BOTTOM",
    "BY","CALL","CANCEL","CBL","CHARACTER","CHARACTERS","CLASS","CLOSE","CODE-SET",
    "COLLATING","COMMA","COMMON","COMP","COMP-1","COMP-2","COMP-3","COMP-4","COMPUTATIONAL",
    "COMPUTATIONAL-1","COMPUTATIONAL-2","COMPUTATIONAL-3","COMPUTATIONAL-4",
    "COMPUTE","CONFIGURATION","CONTAINS","CONTENT","CONTINUE","CONVERTING",
    "COPY","CORR","CORRESPONDING","COUNT","CURRENCY","DATA","DATE","DATE-COMPILED",
    "DATE-WRITTEN","DAY","DAY-OF-WEEK","DBCS","DEBUGGING","DECIMAL-POINT","DECLARATIVES",
    "DELETE","DELIMITED","DELIMITER","DEPENDING","DESCENDING","DISPLAY","DISPLAY-1",
    "DIVIDE","DIVISION","DOWN","DUPLICATES","DYNAMIC","EBCDIC","EGCS","EJECT","ELSE",
    "END","END-ADD","END-CALL","END-COMPUTE","END-DELETE","END-DIVIDE","END-EVALUATE",
    "END-IF","END-MULTIPLY","END-OF-PAGE","END-PERFORM","END-READ","END-RETURN",
    "END-REWRITE","END-SEARCH","END-START","END-STRING","END-SUBTRACT","END-UNSTRING",
    "END-WRITE","ENDING","ENTRY","ENVIRONMENT","EOP","EQUAL","ERROR","EVALUATE",
    "EVERY","EXCEPTION","EXIT","EXTEND","EXTERNAL","FALSE","FD","FILE","FILE-CONTROL",
    "FILLER","FIRST","FOOTING","FOR","FROM","FUNCTION","GENERATE","GIVING","GLOBAL",
    "GO","GOBACK","GREATER","HIGH-VALUE","HIGH-VALUES","I-O","I-O-CONTROL","ID",
    "IDENTIFICATION","IF","IN","INDEX","INDEXED","INITIAL","INITIALIZE","INPUT",
    "INPUT-OUTPUT","INSPECT","INSTALLATION","INTO","INVALID","IS","JUST","JUSTIFIED",
    "KANJI","KEY","LABEL","LEADING","LEFT","LENGTH","LESS","LINAGE","LINAGE-COUNTER",
    "LINE","LINES","LINKAGE","LOCK","LOW-VALUE","LOW-VALUES","MEMORY","MERGE","MODE",
    "MODULES","MORE-LABELS","MOVE","MULTIPLE","MULTIPLY","NATIVE","NEGATIVE",
    "NEXT","NO","NOT","NULL","NULLS","NUMERIC","NUMERIC-EDITED","OBJECT-COMPUTER",
    "OCCURS","OF","OFF","OMITTED","ON","OPEN","OPTIONAL","OR","ORDER","ORGANIZATION",
    "OTHER","OUTPUT","OVERFLOW","PACKED-DECIMAL","PADDING","PAGE","PARSE","PASSWORD",
    "PERFORM","PIC","PICTURE","POINTER","POSITION","POSITIVE","PROCEDURE","PROCEDURE-POINTER",
    "PROCEDURES","PROCEED","PROCESS","PROGRAM","PROGRAM-ID","QUOTE","QUOTES",
    "RANDOM","READ","RECORD","RECORD-KEY","RECORDING","RECORDS","RECURSIVE","REDEFINES",
    "REEL","REFERENCE","RELATIVE","RELEASE","REMAINDER","REMARKS","REMOVAL","RENAMES",
    "REPLACING","RERUN","RESERVE","RETURN","RETURN-CODE","RETURNING","REVERSED",
    "REWIND","REWRITE","RIGHT","ROUNDED","RUN","SAME","SD","SEARCH","SECTION","SECURITY",
    "SEGMENT-LIMIT","SELECT","SENTENCE","SEPARATE","SEQUENCE","SEQUENTIAL",
    "SET","SIGN","SIZE","SKIP1","SKIP2","SKIP3","SORT","SORT-MERGE","SOURCE-COMPUTER",
    "SPACE","SPACES","SPECIAL-NAMES","STANDARD","STANDARD-1","STANDARD-2","START",
    "STATUS","STOP","STRING","SUBTRACT","SUPPRESS","SYMBOLIC","SYNC","SYNCHRONIZED",
    "TALLYING","TAPE","TEST","THAN","THEN","THROUGH","THRU","TIME","TIMES","TO","TOP",
    "TRAILING","TRUE","TRUETEST","UNIT","UNSTRING","UNTIL","UP","UPON","USAGE","USE",
    "USING","VALUE","VALUES","VARYING","WHEN","WITH","WORDS","WORKING-STORAGE",
    "WRITE","WRITE-ONLY","XML","ZERO","ZEROES","ZEROS"]

COBOL_INTRINSICS=[
     "ABS","ACOS","ANNUITY","ASIN","ATAN","CHAR","CHAR-NATIONAL","COS","SIN","CURRENT-DATE",
     "DATE-OF-INTEGER","DATEVAL","DATE-TO-YYYYMMDD","DAY-TO-YYYYDDD","DAY-OF-INTEGER","DISPLAY-OF",
     "EXP","EXP10","FACTORIAL","FRACTION-PART","INTEGER","INTEGER-OF-BOOLEAN","INTEGER-OF-DATE",
     "INTEGER-OF-DAY","INTEGER-PART","LENGTH","LENGTH-AN","LOG","LOG10","LOWER-CASE",
     "NUMVAL","MAX","MEAN","MEDIAN","MIDRANGE","MIN","MOD","NATIONAL-OF","NUMVAL","NUMVAL-C",
     "ORD","ORD-MAX","ORD-MIN","PRESENT-VALUE","RANDOM","RANGE","REM","REVERSE",
     "SQRT","STANDARD-DEVIATION","SUM","TAN","UNDATE","UPPER-CASE","VARIANCE","WHEN-COMPILED",
     "YEAR-TO-YYYY","YEARWINDOW"]


class IBMCOBOLLexer(RegexLexer):
    """
Pygments Lexer for the Enterprise Cobol for z/OS and embedded Db2/Cics/DLi features
        Many early programming languages, including Fortran, Cobol and the various IBM assembler languages,
        used only the first 7-72 columns of a 80-column card

 MAINFRAME COBOL CODING FORM:
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
   Code the PROCESS statement before the IDENTIFICATION DIVISION header and before
   any comment lines or compiler-directing statements. """
    
    def __init__(self, **options):
        RegexLexer.__init__(self, **options)
        self.stripnl=False
        self.stripall=False

    name = 'ibmcobol'
    aliases = ['cobol','ibmcob','ibm_cob', 'IBM_COBOL']
    filenames = ['*.cbl','*.CBL','*.cob','*.COB']
    mimetypes = ["text/x-cobol"]
    flags = re.IGNORECASE | re.DOTALL | re.MULTILINE 

    start_boundarie=r"(?<![-_])\b"
    end_boundarie  =r"(?=\b[^-_])"
    
    # $TODO merge this ! ( due to ambiguity issue with numbers in sdf2 grammar)
    cobol_name=  r'(([0-9]+[\-\_][0-9\-\_]*[A-Za-z][A-Za-z0-9\-\_]*[A-Za-z0-9])' +\
                 r'|([0-9]+[\-][A-Za-z0-9\-\_]*)'                                +\
                 r'|([0-9]*[A-Za-z][A-Za-z0-9\-\_]*[A-Za-z0-9]*))'       

    #(?!.{0,7}\n) => no match in right margin 
    #(?<=\n.{7})  => match after left margin

    custom_tag = "MyTag"

    # My custom tags in left margin
    custom_marge_tag0 = r"\(\^[^_^w]\^\)"
    custom_marge_tag1 = r"\(\^_\^\)"
    custom_marge_tag2 = r"\(\^w\^\)"
    
    tokens = {
     'root': [
               include('special-in-cobol-tag'),
               (r"(^\s*(CBL|PROCESS)[^\n]*)",  Name.CompileOpts) ,
               (r"(^.{6})([\*\/].{65})(.{8})",
                 bygroups(Comment.MargeLeft, Comment, Comment.MargeRight)),
               (r"(^.{6})([D].{65})(.{8})",
                 bygroups(Comment.MargeLeft, Comment.Debug, Comment.MargeRight)),
               (r"(^.{6})([ -])",
                bygroups(Comment.MargeLeft ,Comment.Continuation), 'cobol-content') ,
             ],

    'cobol-content': [
        #include('special-in-cobol-tag'),
                 (r'[^\n]{1,8}\n',   Comment.MargeRight, '#pop'),
                 (r'EXEC\s*SQL\s*',  Comment.SqlExec, 'sql-content'),
                 (r'EXEC\s*CICS\s*', Comment.SqlExec,'cics-content'),
                 (r'EXEC\s*DLI\s*',  Comment.SqlExec, 'dli-content'),
                 include('sec-div'),
                 include('paragraphe'),
                 include('intrinsics'),
                 include('strings'),
                 include('ponctuation'),
                 include('keywords'),
                 include('variable'),
                 include('numbers'), # numbers after variables !
                 include('operator'), # operators after variables ! 
                 (r'[ ]+', Text)
                ],

      'sec-div':[
                     (r'(DECLARATIVES|END\s+DECLARATIVES)', Name.Division),
                     (r'([a-zA-Z0-9-_]+\s+DIVISION)', Name.Division),
                     (r'([a-zA-Z0-9-_]+\s+SECTION)', Name.Section)
                     ],

      'paragraphe':[
                     (r'((?<=\n.{7})(?!(SKIP.? |EJECT |EXEC |COPY ))[a-zA-Z0-9-_]+)(?=\s*[.])',
                         Name.Paragraphe)
                    ],
 
      'keywords':[
           ( start_boundarie + '(' + '|'.join(COBOL_KEYWORDS) + ')' + end_boundarie , Keyword),
            (r'([\=\<\>])',Keyword) 
            ],

      'variable': [
            (cobol_name,Name) 
            ],

      'operator': [(r'((?!.{0,7}\n)[\/\+\-\*])',Operator) ],

      'ponctuation': [
            (r'([~&\^#\|\[\]`!@;,\.():])',Punctuation) ],
 
      'intrinsics': [
          (r'FUNCTION\s*' + start_boundarie +
            '(' + '|'.join(COBOL_INTRINSICS) + ')' + end_boundarie, Name.Function)
            ],

      'strings': [
             (r"(\b[xXzZ])?'[^'\\\n]*(\\.[^'\\\n]*)*'?", String.Single),
             (r'(\b[xXzZ])?"[^"\\\n]*(\\.[^"\\\n]*)*"?', String.Double),
           ],

      'numbers': [
             (r'[+-]?\d+(?![A-Z-_])', Number),
             (r'[+-]?\d*\.\d+([eE][-+]?\d+)?', Number),
             (r'[+-]?\d+\.\d*([eE][-+]?\d+)?', Number)
           ],       

     'dli-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.DliExec,'#pop'),
            (start_boundarie + '(' + '|'.join(DLI_KEYWORDS) + ')' + end_boundarie, Keyword.Dli),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
            include('numbers'),
            include('strings'),
            (cobol_name,Name.Dli), 
            (r'[;:()\[\],\.]', Punctuation.Dli),

        ],

     'cics-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.CicsExec,'#pop'),
            (start_boundarie + '(' + '|'.join(CICS_KEYWORDS) + ')' + end_boundarie, Keyword.Cics),
            (r'[+*/<>=~!@#%^&|`?^-]', Operator),
            include('numbers'),
            include('strings'),
            (cobol_name,Name.Cics), 
            (r'[;:()\[\],\.]', Punctuation.Cics),
        ],
     
     'sql-content': [
            include('special-in-exec-tag'),
            include('comments'),
            (r'END-EXEC',Comment.SqlExec,'#pop'),
            (r'--.*?\n', Comment),
            (start_boundarie + '(' + '|'.join(DB2_KEYWORDS) + ')' + end_boundarie, Keyword.Sql),
            (r'(?!.{0,7}\n)[+*/<>=~!@#%^&|`?^-]', Operator.Sql),
            include('numbers'),
            include('strings'),
            (cobol_name,Name.Sql), 
            (r'[;:()\[\],\.]', Punctuation.Sql),     
               ],

   'comments': [
            (r'(?<=\n).{6}', Comment.MargeLeft),
            (r'[^\n]{0,8}\n', Comment.MargeRight),
            (r'(?<=\n.{6})\*.*?\n', Comment),
            (r'\s+', Text)
              ],    


   'special-in-cobol-tag': [
            (r"(^" + custom_tag + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation),'cobol-content'),
            (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.ScrubolTag, Comment.Continuation),'cobol-content'), 
             include('mytags'),
            ],

   'special-in-exec-tag': [
            (r"(^" + custom_tag + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation)), 
            (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.ScrubolTag, Comment.Continuation)), 
            include('mytags')
              ],
 
 'mytags': [
             (r"(^" + custom_marge_tag0 + r")(.[^\*])",
              bygroups(Text.Tag, Comment.Continuation)), 
            (r"(^" + custom_marge_tag0 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTag, Text.Scrubol)),
            (r"(^" + custom_marge_tag1 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTagDoc, Text.ScrubolDoc)),
            (r"(^" + custom_marge_tag2 + r")(.\*.*?\n)",
                 bygroups(Text.ScrubolTagWarn, Text.ScrubolWarn)),
         ],
    }

if __name__ == "__main__":
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from os.path import abspath
    my_code="""
cbl rent,data(31),lib                                                           
       Identification Division.                                                 
MyTag  Program-id. horror.                                                     
       Author . datim.                                                          
       REMARKS. PROGRAMME VRAIMENT HORRIBLE: \tˇ²°²²¹¹¹\t.                                           
(^w^) *  special cobol tag ! *******************************************70B003
(^.^) *  special cobol tag ! *******************************************70B003
(^_^) *  special cobol tag ! *******************************************70B003
(^x^) *  special cobol tag ! *******************************************70B003
(^ ^) *  special cobol tag ! *******************************************70B003
       DATE-WRITTEN. AOUT 2010                                                  
       Environment Division .
       Configuration Section .
       Source-Computer.                                                         
(^?^)            IBM-370.                                                             
       Object-computer.                                                         
           IBM-370.                                                             
       Special-names .
           Decimal-point Is Comma .
       Input-output Section .
       File-control.
           Select FFFFFGS Assign  FFFFFGS
             Organization  Indexed
             Access Mode  Dynamic 
             Record Key  FFFFFGS-CLE  
             File Status  W-FFFFFGS-STATUS  .
       Data Division.
       File Section.
       Fd FFFFFGS 
MyTag           Label Record  Standard
MyTag           Data Record  FFFFFGS-ENREG.
       Copy FFFFFFGS.
       Working-storage Section.                                                 
       01 8-9bytes.                                                           
       01 98-9bytes.                                                           
''''''      05 four-bytes pic x.                                                           
pic        03 fives-bytes pic x.                                                           
       01 filler   Pic  s9(9)  Binary.                                        
       01 filler-x Pic  s9(9)  Binary.                                        
       05 ptr4  Redefines full-word  Pointer.                                   
       05 hexstr          pic X(4) value 'xxxx'.                                
007220******************************************************************70B003  
007230*** DéCLARE CURSEUR TABLE MH37=AFFVEAP (C-MH37)                   70B004  
007240******************************************************************70B005  
007250     EXEC SQL                                                     COMP.DB2
''''''       DECLARE C-MH37-U CURSOR   FOR                              COMP.DB2
007270       SELECT                                                     70B008  
(^@^)             A.COETBL , A.COTNET                                   70B011  
007430       FROM AFFVEAP   A                                           COMP.DB2
MyTag        WHERE                                                      COMP.DB2
007450*A.COETBL = :MH37-COETBLAND                                       COMP.DB2
007450 A.COTNET LIKE 'ET%'                                              COMP.DB2
'''''' A.COTNET > 'ETx'                                                 COMP.DB2
007520       FOR UPDATE OF                                              70B504  
007530          COTNET                                                  COMP.DB2
(^w^) *      OPTIMIZE FOR 1 ROWS                                        COMP.DB2
007550     END-EXEC.                                                    COMP.DB2
           01 PFKEY-INDICATOR  VALUE 00  PIC 99.                                
              88 ENTER-KEY VALUE 00.       88 CLEAR VALUE 93.                   
              88 PA1   VALUE 92. 88 PA2   VALUE 94. 88 PA3   VALUE 91.          
              88 PFK1  VALUE 1.  88 PFK2  VALUE 2.  88 PFK3  VALUE 3.           
       SKIP1                                                                    

000000 Linkage Section.                                                         
       05 hexstr          pic X(4) value 'xxxx'.                                
007220******************************************************************70B003
       05 ptr1   Pointer Occurs 256.                                            
(^@^)  Procedure Division Using ZC-COMM                                         
                                TABLE-P       .                                 
       DANGLING-ELSE.                                                   00394818
           Exec Cics        
(^@^)             LINK PROGRAM (ZL00-LCPG8) COMMAREA (ZL99-LICOA) LENGTH        
MyTag             (ZL00-QLENR)        
           End-exec.        
           if cond1 greater or equal 1                                  00394819
             THEN DISPLAY 'COND1>='                                             
              if cond2 LESS THAN 10                                     00394819
                display 'cond2'                                                 
           else                                                         00394819
MyTag       display 'else cond1?'                                             
           else                                                                 
           Set Address Of cb1 To Null                                           
         Move  cb1(2:full-word)  To user-name .
         EXEC DLI GU USING PCB(PCBNUM)
             SEGMENT((SEGNAME))
FIX000           KEYS(CONKEYB) KEYLENGTH(8) SETPARENT
(^.^) * ===>  
FIX000              SEGMENT(SEGC) INTO(AREAC) SEGLENGTH(SEGLEN)
(^w^) * ===>  qualified ssa :
FIX000              WHERE(KEYC=SEGKEYC) FIELDLENGTH(4) END-EXEC.
         
"""
    test='cobol_test.html'
    highlight(''.join([l.ljust(80) + '\n'
                       for l in my_code.splitlines()]), # enforce 80 columns
              IBMCOBOLLexer(encoding='utf-8')
             ,HtmlFormatter(style=IBMCOBOLStyle
                            ,encoding='utf-8'
                            #,noclasses=True
                            ,full=True
                            ,cssfile='ibmcob.css'
                            #,noclobber_cssfile=True
                            ,linenos='inline'
                            ,title='Test pygments IBM Cobol Lexer '
                            ,monofont=True)
             ,open(test,'wb'))
    
    print "file://"+abspath(test),
    
