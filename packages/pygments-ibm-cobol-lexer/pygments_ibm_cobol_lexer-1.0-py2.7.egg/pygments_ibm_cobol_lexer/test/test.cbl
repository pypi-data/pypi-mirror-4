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
         

